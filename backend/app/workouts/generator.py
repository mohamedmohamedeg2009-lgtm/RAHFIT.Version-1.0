from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

import structlog

from app.ai.exceptions import AIProviderError, AISafetyError
from app.ai.schemas import AIServiceRequest
from app.ai.service import AIService
from app.models.ai_classifier import AICapabilityClassificationResult, AIClassificationReasonCode
from app.models.ai_context import AIContextPurpose, AIContextRequest
from app.models.ai_policy import AIAction, AICapability
from app.models.user import User
from app.models.workout import Equipment
from app.readiness.checker import ReadinessChecker
from app.readiness.models import ReadinessSeverity
from app.services.ai_policy import AIPolicyService
from app.users.service import UserIntelligenceService
from app.workouts.exceptions import (
    WorkoutExerciseUnavailableError,
    WorkoutHealthProfileIncompleteError,
    WorkoutMedicalClearanceRequiredError,
    WorkoutProfileIncompleteError,
    WorkoutReadinessBlockedError,
)
from app.workouts.exercises.catalog import ExerciseCatalog
from app.workouts.exercises.models import CatalogExercise, ExerciseCategory, MovementPattern
from app.workouts.exercises.selector import ExerciseSelector, SelectionContext, SelectionResult
from app.workouts.models import (
    GenerationMode,
    PlannedExercise,
    SectionType,
    SetPrescription,
    WorkoutDay,
    WorkoutExplanation,
    WorkoutGenerationMetadata,
    WorkoutPlan,
    WorkoutSection,
    WorkoutWarning,
)
from app.workouts.planner import WorkoutPlanner
from app.workouts.prompts.workout_generation import build_workout_enhancement_instructions
from app.workouts.rules import RULES_VERSION
from app.workouts.schemas import AIWorkoutEnhancement, WorkoutGenerationRequest
from app.workouts.validator import WorkoutValidator


class WorkoutGenerator:
    """Creates a valid Python-owned base plan before optional AI explanation."""

    def __init__(
        self,
        *,
        intelligence: UserIntelligenceService,
        readiness: ReadinessChecker,
        planner: WorkoutPlanner,
        catalog: ExerciseCatalog,
        selector: ExerciseSelector,
        validator: WorkoutValidator,
        ai_service: AIService | None = None,
        id_factory: Callable[[], str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.intelligence = intelligence
        self.readiness = readiness
        self.planner = planner
        self.catalog = catalog
        self.selector = selector
        self.validator = validator
        self.ai_service = ai_service
        self.id_factory = id_factory or (lambda: str(uuid4()))
        self.clock = clock or (lambda: datetime.now(UTC))
        self.logger = structlog.get_logger("app.workouts.generator")

    async def generate(self, user: User, request: WorkoutGenerationRequest) -> WorkoutPlan:
        started = perf_counter()
        snapshot = await self.intelligence.get_snapshot(user.id)
        if snapshot.profile is None:
            raise WorkoutProfileIncompleteError()
        if snapshot.health_profile is None:
            raise WorkoutHealthProfileIncompleteError()
        readiness = self.readiness.check(snapshot)
        if not readiness.ready_for_ai:
            self.logger.warning(
                "workout_generation_blocked",
                user_id=user.id,
                readiness_decision=readiness.status.value,
                reason_codes=tuple(item.code for item in readiness.issues),
            )
            if any(
                item.code.startswith("health.") and item.requires_professional_guidance
                for item in readiness.issues
            ):
                raise WorkoutMedicalClearanceRequiredError()
            raise WorkoutReadinessBlockedError(readiness.status.value)

        profile = snapshot.profile
        health = snapshot.health_profile
        constraints = self.planner.create_constraints(snapshot, readiness)
        rejected: Counter[str] = Counter()
        days: list[WorkoutDay] = []
        total_selected = 0
        remaining_weekly_sets = constraints.maximum_weekly_sets
        for template in constraints.days:
            used: set[str] = set()
            sections: list[WorkoutSection] = []
            section_specs = [
                (SectionType.WARMUP, (MovementPattern.MOBILITY,)),
                (SectionType.MAIN, template.main_patterns),
                (SectionType.ACCESSORY, template.accessory_patterns),
            ]
            if template.include_conditioning:
                section_specs.append((SectionType.CONDITIONING, (MovementPattern.CONDITIONING,)))
            section_specs.append((SectionType.COOLDOWN, (MovementPattern.MOBILITY,)))

            for section_type, patterns in section_specs:
                selection_context = SelectionContext(
                    equipment=frozenset(profile.training.available_equipment),
                    locations=constraints.locations,
                    experience=profile.training.experience,
                    age_group=profile.age_group,
                    goal=profile.goals.primary_goal,
                    injury_areas=frozenset(
                        item.area.lower() for item in health.injuries if item.active
                    ),
                    pain_areas=frozenset(
                        item.area.lower() for item in health.pain_areas if item.intensity > 0
                    ),
                    mobility_limitations=frozenset(
                        item.area.lower() for item in health.mobility_limitations
                    ),
                    chronic_conditions=frozenset(
                        item.name.lower() for item in health.chronic_conditions
                    ),
                    medically_cleared=not health.requires_medical_clearance,
                    remaining_minutes=constraints.session_minutes,
                    remaining_weekly_sets=remaining_weekly_sets,
                    excluded_ids=frozenset(used),
                )
                result = self.selector.select(
                    self._catalog_for(section_type),
                    selection_context,
                    patterns,
                )
                self._record_rejections(rejected, result)
                if not result.selected and section_type == SectionType.MAIN:
                    result = self.selector.select(
                        self._catalog_for(section_type),
                        selection_context,
                        (
                            MovementPattern.SQUAT,
                            MovementPattern.HINGE,
                            MovementPattern.PUSH,
                            MovementPattern.PULL,
                            MovementPattern.LUNGE,
                            MovementPattern.CARRY,
                            MovementPattern.CORE,
                            MovementPattern.ROTATION,
                        ),
                    )
                    self._record_rejections(rejected, result)
                if not result.selected:
                    if section_type in {SectionType.ACCESSORY, SectionType.CONDITIONING}:
                        continue
                    raise WorkoutExerciseUnavailableError(
                        f"workout_no_safe_{section_type.value}_exercise"
                    )
                selected = result.selected[:4]
                alternatives = {
                    item.selected_exercise_id: item.approved_alternative_ids
                    for item in result.alternatives
                }
                used.update(item.id for item in selected)
                planned = tuple(
                    self._planned(
                        item,
                        constraints.prescription,
                        section_type,
                        profile.training.available_equipment,
                        alternatives.get(item.id, ()),
                    )
                    for item in selected
                )
                remaining_weekly_sets -= sum(item.prescription.sets for item in planned)
                sections.append(WorkoutSection(section_type=section_type, exercises=planned))

            estimate = sum(section.estimated_duration_minutes for section in sections)
            exercise_count = sum(len(section.exercises) for section in sections)
            if (
                estimate > constraints.session_minutes
                or exercise_count > constraints.maximum_session_exercises
                or exercise_count < constraints.minimum_session_exercises
            ):
                raise WorkoutExerciseUnavailableError("workout_session_constraints_unsatisfied")
            total_selected += exercise_count
            days.append(
                WorkoutDay(
                    day_number=template.day_number,
                    weekday=template.weekday,
                    title=f"Day {template.day_number}: {template.focus}",
                    focus=template.focus,
                    estimated_duration_minutes=max(15, estimate),
                    sections=tuple(sections),
                    recovery_notes=(
                        "Keep at least the planned recovery spacing before similar loading.",
                        "Prioritize sleep and hydration before progressing volume.",
                    ),
                    high_intensity=template.high_intensity,
                )
            )

        warnings = tuple(
            WorkoutWarning(
                code=item.code,
                message=item.message,
                professional_guidance=item.requires_professional_guidance,
            )
            for item in readiness.issues
            if item.severity == ReadinessSeverity.WARNING
        )
        now = self.clock()
        plan = WorkoutPlan(
            plan_id=self.id_factory(),
            user_id=user.id,
            primary_goal=profile.goals.primary_goal,
            secondary_goal=profile.goals.secondary_goal,
            plan_type=constraints.plan_type,
            experience_level=profile.training.experience,
            location=profile.training.workout_location,
            equipment=profile.training.available_equipment,
            duration_weeks=request.duration_weeks,
            training_days_per_week=len(days),
            weekly_schedule=tuple(days),
            warnings=warnings,
            safety_notes=(
                "Stop exercise if pain, dizziness, chest pain, or unusual symptoms occur.",
                "Seek qualified professional guidance for medical concerns.",
            ),
            progression_guidance=(
                "Progress only after completing prescribed work with controlled technique.",
                "Increase one variable at a time by no more than the prescription limit.",
            ),
            explanation=WorkoutExplanation(
                summary=(
                    "A deterministic plan built from approved profile, readiness, and "
                    "health constraints."
                ),
                rationale=(
                    "Movement balance, recovery, equipment, experience, and safety "
                    "exclusions were enforced by Python rules.",
                ),
                motivation="Consistency and safe technique are the priority.",
            ),
            generation_metadata=WorkoutGenerationMetadata(
                mode=GenerationMode.DETERMINISTIC,
                catalog_version=self.catalog.version,
                rules_version=RULES_VERSION,
                readiness_status=readiness.status,
                generation_key=constraints.generation_key,
                selected_exercise_count=total_selected,
                rejected_by_reason=dict(rejected),
            ),
            generated_at=now,
            activated_at=now,
            updated_at=now,
        )
        validation = self.validator.validate(plan, snapshot, self.catalog)
        self.validator.raise_for_result(validation)
        plan = plan.model_copy(
            update={
                "generation_metadata": plan.generation_metadata.model_copy(
                    update={"validation_codes": validation.validation_codes}
                )
            }
        )

        if request.use_ai_assistance:
            plan = await self._enhance(user, plan)
            self.validator.validate_or_raise(plan, snapshot, self.catalog)

        self.logger.info(
            "workout_plan_generated",
            user_id=user.id,
            plan_id=plan.plan_id,
            readiness_decision=readiness.status.value,
            selected_goal=profile.goals.primary_goal.value,
            training_days=plan.training_days_per_week,
            selected_exercise_count=total_selected,
            rejected_exercise_counts=dict(rejected),
            generation_mode=plan.generation_metadata.mode.value,
            validation_outcome="valid",
            fallback_reason=plan.generation_metadata.fallback_reason,
            latency_ms=round((perf_counter() - started) * 1000),
        )
        return plan

    @staticmethod
    def _record_rejections(counter: Counter[str], result: SelectionResult) -> None:
        for rejection in result.rejections:
            counter.update(reason.value for reason in rejection.reasons)

    def _catalog_for(self, section: SectionType) -> tuple[CatalogExercise, ...]:
        categories = {
            SectionType.WARMUP: {ExerciseCategory.WARMUP},
            SectionType.MAIN: {ExerciseCategory.STRENGTH, ExerciseCategory.POWER},
            SectionType.ACCESSORY: {ExerciseCategory.STRENGTH},
            SectionType.CONDITIONING: {ExerciseCategory.CARDIO},
            SectionType.COOLDOWN: {ExerciseCategory.COOLDOWN},
        }[section]
        return tuple(item for item in self.catalog.all() if item.category in categories)

    @staticmethod
    def _planned(
        exercise: CatalogExercise,
        prescription: SetPrescription,
        section: SectionType,
        available_equipment: tuple[Equipment, ...],
        alternatives: tuple[str, ...],
    ) -> PlannedExercise:
        applied = (
            prescription
            if section in {SectionType.MAIN, SectionType.ACCESSORY}
            else SetPrescription(
                sets=1,
                min_reps=exercise.default_rep_range[0],
                max_reps=exercise.default_rep_range[1],
                rest_seconds=30,
                rpe_min=3,
                rpe_max=5,
                reps_in_reserve=5,
                progression_limit_percentage=0,
            )
        )
        equipment = (
            exercise.equipment
            if exercise.requires_all_equipment
            else tuple(item for item in exercise.equipment if item in available_equipment)[:1]
        )
        return PlannedExercise(
            exercise_id=exercise.id,
            exercise_name=exercise.name,
            movement_pattern=exercise.movement_pattern,
            primary_muscles=exercise.primary_muscles,
            equipment=equipment,
            prescription=applied,
            estimated_duration_minutes=exercise.estimated_duration_minutes,
            alternatives=alternatives,
            instructions=exercise.instructions,
            safety_notes=exercise.safety_notes,
        )

    async def _enhance(self, user: User, plan: WorkoutPlan) -> WorkoutPlan:
        ai_service = self.ai_service
        if ai_service is None:
            return self._fallback(plan, "ai_service_unavailable")
        classification = AICapabilityClassificationResult(
            capability=AICapability.EXPLAIN_WORKOUT,
            confidence=1,
            matched_rules=("trusted_workout_engine",),
            reason_code=AIClassificationReasonCode.WORKOUT_INTENT_MATCHED,
            requires_safety_review=True,
        )
        policy = AIPolicyService().evaluate(AICapability.EXPLAIN_WORKOUT, AIAction.EXPLAIN)
        try:
            response = await ai_service.generate_json(
                user,
                AIServiceRequest(
                    prompt="Explain my validated workout plan.",
                    system_instructions=build_workout_enhancement_instructions(plan),
                    context_request=AIContextRequest(purpose=AIContextPurpose.EXPLAIN_WORKOUT_PLAN),
                    classification=classification,
                    policy=policy,
                ),
                AIWorkoutEnhancement,
            )
            enhanced = response.output
            approved = tuple(
                item.exercise_id
                for day in plan.weekly_schedule
                for section in day.sections
                for item in section.exercises
            )
            if enhanced.approved_exercise_ids != approved:
                return self._fallback(plan, "ai_exercise_allow_list_mismatch")
            return plan.model_copy(
                update={
                    "explanation": enhanced.explanation,
                    "generation_metadata": plan.generation_metadata.model_copy(
                        update={
                            "mode": GenerationMode.AI_ASSISTED,
                            "provider": response.provider,
                            "model": response.model,
                        }
                    ),
                }
            )
        except (AIProviderError, AISafetyError) as exc:
            return self._fallback(plan, type(exc).__name__)

    def _fallback(self, plan: WorkoutPlan, reason: str) -> WorkoutPlan:
        self.logger.warning(
            "workout_ai_fallback",
            user_id=plan.user_id,
            plan_id=plan.plan_id,
            fallback_reason=reason,
        )
        return plan.model_copy(
            update={
                "generation_metadata": plan.generation_metadata.model_copy(
                    update={
                        "mode": GenerationMode.DETERMINISTIC_FALLBACK,
                        "fallback_reason": reason,
                        "provider": None,
                        "model": None,
                    }
                )
            }
        )
