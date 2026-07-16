from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.models.assessment import AssessmentResult, SafetyStatus
from app.models.dashboard import (
    DashboardAction,
    DashboardActionType,
    DashboardAssessmentStatus,
    DashboardAssessmentSummary,
    DashboardFeature,
    DashboardFreshness,
    DashboardMetadata,
    DashboardProgressSnapshot,
    DashboardSafetyNotice,
    DashboardSeverity,
    DashboardUserSummary,
    DashboardView,
    FeatureStatus,
)
from app.models.nutrition import NutritionDashboardState
from app.models.user import User
from app.models.workout import WorkoutDashboardState
from app.services.assessment import SessionState


class DashboardAssessmentReader(Protocol):
    async def get_active_assessment(self, user_id: str) -> SessionState | None: ...

    async def get_latest_assessment_optional(self, user_id: str) -> AssessmentResult | None: ...


class DashboardWorkoutReader(Protocol):
    async def get_dashboard_state(self, user_id: str) -> WorkoutDashboardState | None: ...


class DashboardNutritionReader(Protocol):
    async def dashboard(self, user_id: str) -> NutritionDashboardState | None: ...


class DashboardOwnershipError(Exception):
    """Raised when an internal source violates the owner-scoped reader contract."""


class DashboardService:
    """Aggregate owner-scoped dashboard state and select one explainable next action."""

    VERSION = "1.1"
    REASSESSMENT_AFTER = timedelta(days=90)

    def __init__(
        self,
        assessment: DashboardAssessmentReader,
        workout: DashboardWorkoutReader | None = None,
        nutrition: DashboardNutritionReader | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.assessment = assessment
        self.workout = workout
        self.nutrition = nutrition
        self.clock = clock or (lambda: datetime.now(UTC))

    async def get_dashboard(self, user: User) -> DashboardView:
        now = self.clock()
        active: SessionState | None = None
        result: AssessmentResult | None = None
        partial_data = False
        workout_state: WorkoutDashboardState | None = None
        nutrition_state: NutritionDashboardState | None = None
        try:
            active = await self.assessment.get_active_assessment(user.id)
            if active and active.session.user_id != user.id:
                raise DashboardOwnershipError
            if not active:
                result = await self.assessment.get_latest_assessment_optional(user.id)
                if result and result.user_id != user.id:
                    raise DashboardOwnershipError
        except DashboardOwnershipError:
            raise
        except Exception:
            # Optional failures must not expose infrastructure details or blank the page.
            partial_data = True

        if self.workout and not partial_data:
            try:
                workout_state = await self.workout.get_dashboard_state(user.id)
            except Exception:
                partial_data = True
        if self.nutrition and not partial_data:
            try:
                nutrition_state = await self.nutrition.dashboard(user.id)
            except Exception:
                partial_data = True

        status = self._assessment_status(active, result, partial_data)
        profile_completeness, missing_profile_fields = self._profile_state(user)
        assessment_summary = self._assessment_summary(active, result, partial_data, now)
        user_summary = DashboardUserSummary(
            display_name=user.display_name or self._display_name_from_email(user.email),
            primary_goal=self._primary_goal(active, result),
            preferred_units=user.preferred_units or "metric",
            assessment_status=status,
            profile_completeness=profile_completeness,
            missing_profile_fields=missing_profile_fields,
        )
        priority = self._daily_priority(
            assessment_summary,
            workout_state,
            profile_completeness,
            partial_data,
            self.workout is not None,
        )
        return DashboardView(
            user=user_summary,
            assessment=assessment_summary,
            workout=workout_state,
            nutrition=nutrition_state,
            daily_priority=priority,
            features=self._features(
                assessment_summary,
                workout_state,
                nutrition_state,
                partial_data,
                self.workout is not None,
                self.nutrition is not None,
            ),
            safety_notice=self._safety_notice(active, result),
            progress=DashboardProgressSnapshot(
                assessment_completion=assessment_summary.completion_percentage,
                profile_completeness=profile_completeness,
                latest_readiness_score=assessment_summary.readiness_score,
                last_activity_date=self._last_activity(active, result),
            ),
            quick_actions=self._quick_actions(
                assessment_summary,
                workout_state,
                missing_profile_fields,
                self.workout is not None,
            ),
            metadata=DashboardMetadata(
                generated_at=now,
                data_freshness=(
                    DashboardFreshness.PARTIAL if partial_data else DashboardFreshness.LIVE
                ),
                partial_data=partial_data,
                dashboard_version=self.VERSION,
            ),
        )

    @staticmethod
    def _display_name_from_email(email: str) -> str:
        local_part = email.partition("@")[0].replace(".", " ").replace("_", " ").strip()
        return local_part.title() or "RAHFIT member"

    @staticmethod
    def _profile_state(user: User) -> tuple[int, tuple[str, ...]]:
        fields = {
            "email": bool(user.email),
            "display_name": bool(user.display_name),
            "preferred_units": bool(user.preferred_units),
        }
        missing = tuple(field for field, present in fields.items() if not present)
        complete = round(sum(fields.values()) / len(fields) * 100)
        return complete, missing

    @staticmethod
    def _assessment_status(
        active: SessionState | None,
        result: AssessmentResult | None,
        partial_data: bool,
    ) -> DashboardAssessmentStatus:
        if partial_data:
            return DashboardAssessmentStatus.UNAVAILABLE
        if active:
            return DashboardAssessmentStatus.IN_PROGRESS
        if result:
            return DashboardAssessmentStatus.COMPLETED
        return DashboardAssessmentStatus.NOT_STARTED

    def _assessment_summary(
        self,
        active: SessionState | None,
        result: AssessmentResult | None,
        partial_data: bool,
        now: datetime,
    ) -> DashboardAssessmentSummary:
        if partial_data:
            return DashboardAssessmentSummary(
                status=DashboardAssessmentStatus.UNAVAILABLE,
                completion_percentage=0,
            )
        if active:
            return DashboardAssessmentSummary(
                status=DashboardAssessmentStatus.IN_PROGRESS,
                session_id=active.session.id,
                completion_percentage=active.progress.assessment_completeness,
                readiness_score=active.progress.readiness_score,
                risk_level=active.progress.safety.risk_level,
                safety_status=active.progress.safety.status,
                missing_categories=active.progress.missing_categories,
            )
        if result:
            generated_at = self._as_utc(result.generated_at)
            return DashboardAssessmentSummary(
                status=DashboardAssessmentStatus.COMPLETED,
                session_id=result.session_id,
                completion_percentage=result.assessment_completeness,
                readiness_score=result.readiness_score,
                risk_level=result.risk_level,
                safety_status=result.safety_status,
                missing_categories=result.missing_categories,
                latest_completion_date=result.generated_at,
                reassessment_recommended=now - generated_at >= self.REASSESSMENT_AFTER,
            )
        return DashboardAssessmentSummary(
            status=DashboardAssessmentStatus.NOT_STARTED,
            completion_percentage=0,
        )

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)

    @staticmethod
    def _primary_goal(active: SessionState | None, result: AssessmentResult | None) -> str | None:
        if active:
            answer = active.session.answers.get("primary_goal")
            return str(answer.value) if answer and isinstance(answer.value, str) else None
        if result:
            value = result.profile.get("goals", {}).get("primary_goal")
            return str(value) if isinstance(value, str) else None
        return None

    @staticmethod
    def _daily_priority(
        assessment: DashboardAssessmentSummary,
        workout: WorkoutDashboardState | None,
        profile_completeness: int,
        partial_data: bool,
        workout_enabled: bool,
    ) -> DashboardAction:
        if partial_data:
            return DashboardAction(
                action_type=DashboardActionType.CONTINUE_AVAILABLE,
                title="Dashboard data needs a refresh",
                description="Your account is available, but some assessment data could not load.",
                destination_route="/app",
                priority_reason="An optional dashboard source is temporarily unavailable.",
                severity=DashboardSeverity.WARNING,
            )
        if assessment.safety_status == SafetyStatus.STOP:
            return DashboardAction(
                action_type=DashboardActionType.REVIEW_SAFETY,
                title="Review your safety notice",
                description=(
                    "Personalized plan preparation is paused pending professional clearance."
                ),
                destination_route=DashboardService._assessment_route(assessment),
                priority_reason="A STOP safety rule takes precedence over every other action.",
                severity=DashboardSeverity.DANGER,
            )
        if assessment.status == DashboardAssessmentStatus.NOT_STARTED:
            return DashboardAction(
                action_type=DashboardActionType.START_ASSESSMENT,
                title="Start your smart assessment",
                description="Tell us about your goals, routine, and safety context.",
                destination_route="/assessment",
                priority_reason="An assessment is required before personalized planning.",
                severity=DashboardSeverity.INFO,
            )
        if assessment.status == DashboardAssessmentStatus.IN_PROGRESS:
            return DashboardAction(
                action_type=DashboardActionType.RESUME_ASSESSMENT,
                title="Continue your assessment",
                description="Resume from your saved answer and complete your readiness profile.",
                destination_route=DashboardService._assessment_route(assessment),
                priority_reason="An unfinished assessment is the closest useful next step.",
                severity=DashboardSeverity.INFO,
            )
        if workout:
            in_progress = workout.status == "in_progress"
            return DashboardAction(
                action_type=(
                    DashboardActionType.CONTINUE_WORKOUT
                    if in_progress
                    else DashboardActionType.START_WORKOUT
                ),
                title="Continue today's workout" if in_progress else "Start today's workout",
                description=f"{workout.title} is ready for you.",
                destination_route=workout.destination_route,
                priority_reason="A safe personalized workout is available today.",
                severity=DashboardSeverity.SUCCESS,
            )
        if workout_enabled and assessment.status == DashboardAssessmentStatus.COMPLETED:
            return DashboardAction(
                action_type=DashboardActionType.GENERATE_WORKOUT,
                title="Create your workout plan",
                description="Use your completed assessment to build a deterministic plan.",
                destination_route="/workouts",
                priority_reason="Your assessment is complete and no active workout plan exists.",
                severity=DashboardSeverity.INFO,
            )
        if profile_completeness < 100:
            return DashboardAction(
                action_type=DashboardActionType.COMPLETE_PROFILE,
                title="Review missing profile preferences",
                description=(
                    "Your assessment is complete; profile preferences are the remaining setup item."
                ),
                destination_route="/app#profile-summary",
                priority_reason="Required profile preferences are incomplete.",
                severity=DashboardSeverity.INFO,
            )
        return DashboardAction(
            action_type=DashboardActionType.VIEW_ASSESSMENT,
            title="Review your assessment summary",
            description="Your completed readiness profile is available to review.",
            destination_route=DashboardService._assessment_route(assessment),
            priority_reason="Assessment is complete and no higher-priority safety action exists.",
            severity=DashboardSeverity.SUCCESS,
        )

    @staticmethod
    def _assessment_route(assessment: DashboardAssessmentSummary) -> str:
        if not assessment.session_id:
            return "/assessment"
        if assessment.status == DashboardAssessmentStatus.COMPLETED:
            return f"/assessment/completed/{assessment.session_id}"
        return f"/assessment/resume/{assessment.session_id}"

    @staticmethod
    def _features(
        assessment: DashboardAssessmentSummary,
        workout: WorkoutDashboardState | None,
        nutrition: NutritionDashboardState | None,
        partial_data: bool,
        workout_enabled: bool,
        nutrition_enabled: bool,
    ) -> tuple[DashboardFeature, ...]:
        if partial_data:
            assessment_feature = DashboardFeature(
                key="assessment",
                title="Smart assessment",
                status=FeatureStatus.ACTION_REQUIRED,
                reason="Assessment status is temporarily unavailable. Refresh before continuing.",
            )
        elif assessment.status == DashboardAssessmentStatus.COMPLETED:
            assessment_feature = DashboardFeature(
                key="assessment",
                title="Smart assessment",
                status=FeatureStatus.AVAILABLE,
                reason="Your latest assessment summary is available.",
                destination_route=DashboardService._assessment_route(assessment),
            )
        else:
            assessment_feature = DashboardFeature(
                key="assessment",
                title="Smart assessment",
                status=FeatureStatus.ACTION_REQUIRED,
                reason=(
                    "Continue your saved assessment."
                    if assessment.status == DashboardAssessmentStatus.IN_PROGRESS
                    else "Complete the assessment to unlock personalized planning."
                ),
                destination_route=DashboardService._assessment_route(assessment),
            )

        safety_locked = assessment.safety_status == SafetyStatus.STOP
        assessment_ready = assessment.status == DashboardAssessmentStatus.COMPLETED

        def future_feature(key: str, title: str) -> DashboardFeature:
            if safety_locked:
                return DashboardFeature(
                    key=key,
                    title=title,
                    status=FeatureStatus.LOCKED,
                    reason="Locked until the safety notice is professionally reviewed.",
                )
            if not assessment_ready:
                return DashboardFeature(
                    key=key,
                    title=title,
                    status=FeatureStatus.LOCKED,
                    reason="Complete the smart assessment first.",
                )
            return DashboardFeature(
                key=key,
                title=title,
                status=FeatureStatus.COMING_SOON,
                reason="This module is planned but is not available in the current release.",
            )

        if not workout_enabled:
            workout_feature = future_feature("workout", "Workout planning")
        elif safety_locked:
            workout_feature = DashboardFeature(
                key="workout",
                title="Workout planning",
                status=FeatureStatus.LOCKED,
                reason="Locked until the safety notice is professionally reviewed.",
            )
        elif not assessment_ready:
            workout_feature = DashboardFeature(
                key="workout",
                title="Workout planning",
                status=FeatureStatus.LOCKED,
                reason="Complete the smart assessment first.",
            )
        elif workout:
            workout_feature = DashboardFeature(
                key="workout",
                title="Workout planning",
                status=FeatureStatus.AVAILABLE,
                reason="Your personalized workout plan is available.",
                destination_route=workout.destination_route,
            )
        else:
            workout_feature = DashboardFeature(
                key="workout",
                title="Workout planning",
                status=FeatureStatus.ACTION_REQUIRED,
                reason="Generate a plan from your completed assessment.",
                destination_route="/workouts",
            )

        if not nutrition_enabled or safety_locked or not assessment_ready:
            nutrition_feature = future_feature("nutrition", "Nutrition planning")
        elif nutrition:
            nutrition_feature = DashboardFeature(
                key="nutrition",
                title="Nutrition planning",
                status=FeatureStatus.AVAILABLE,
                reason=f"{nutrition.calories_remaining} calories remaining today.",
                destination_route="/nutrition",
            )
        else:
            nutrition_feature = DashboardFeature(
                key="nutrition",
                title="Nutrition planning",
                status=FeatureStatus.ACTION_REQUIRED,
                reason="Generate nutrition targets from your assessment.",
                destination_route="/nutrition",
            )

        return (
            assessment_feature,
            workout_feature,
            nutrition_feature,
            future_feature("ai_coach", "AI Coach"),
            future_feature("progress", "Progress tracking"),
            DashboardFeature(
                key="reports",
                title="Reports",
                status=FeatureStatus.LOCKED,
                reason="Reports require sufficient real progress data.",
            ),
        )

    @staticmethod
    def _safety_notice(
        active: SessionState | None, result: AssessmentResult | None
    ) -> DashboardSafetyNotice | None:
        status = (
            active.progress.safety.status
            if active
            else result.safety_status if result else SafetyStatus.SAFE
        )
        explanations = (
            active.progress.safety.explanations
            if active
            else result.safety_explanations if result else ()
        )
        if status == SafetyStatus.SAFE:
            return None
        message = explanations[0] if explanations else "Review your assessment safety guidance."
        if status == SafetyStatus.STOP:
            return DashboardSafetyNotice(
                status=status,
                title="Personalized planning is paused",
                message=message,
                severity=DashboardSeverity.DANGER,
                plan_generation_blocked=True,
            )
        return DashboardSafetyNotice(
            status=status,
            title="Continue with caution",
            message=message,
            severity=DashboardSeverity.WARNING,
            plan_generation_blocked=False,
        )

    @staticmethod
    def _last_activity(
        active: SessionState | None, result: AssessmentResult | None
    ) -> datetime | None:
        if active:
            return active.session.last_activity_at
        return result.generated_at if result else None

    @staticmethod
    def _quick_actions(
        assessment: DashboardAssessmentSummary,
        workout: WorkoutDashboardState | None,
        missing_profile_fields: tuple[str, ...],
        workout_enabled: bool,
    ) -> tuple[DashboardAction, ...]:
        actions: list[DashboardAction] = []
        if workout_enabled and assessment.status == DashboardAssessmentStatus.COMPLETED:
            actions.append(
                DashboardAction(
                    action_type=(
                        DashboardActionType.CONTINUE_WORKOUT
                        if workout and workout.status == "in_progress"
                        else (
                            DashboardActionType.START_WORKOUT
                            if workout
                            else DashboardActionType.GENERATE_WORKOUT
                        )
                    ),
                    title="Open today's workout" if workout else "Create workout plan",
                    description="Open your personalized training experience.",
                    destination_route=workout.destination_route if workout else "/workouts",
                    priority_reason="Workout planning is available after assessment completion.",
                    severity=DashboardSeverity.INFO,
                )
            )
        if assessment.status != DashboardAssessmentStatus.UNAVAILABLE:
            action_type = (
                DashboardActionType.START_ASSESSMENT
                if assessment.status == DashboardAssessmentStatus.NOT_STARTED
                else (
                    DashboardActionType.RESUME_ASSESSMENT
                    if assessment.status == DashboardAssessmentStatus.IN_PROGRESS
                    else DashboardActionType.VIEW_ASSESSMENT
                )
            )
            actions.append(
                DashboardAction(
                    action_type=action_type,
                    title=(
                        "Start assessment"
                        if action_type == DashboardActionType.START_ASSESSMENT
                        else (
                            "Resume assessment"
                            if action_type == DashboardActionType.RESUME_ASSESSMENT
                            else "View assessment result"
                        )
                    ),
                    description="Open the assessment experience.",
                    destination_route=DashboardService._assessment_route(assessment),
                    priority_reason="This action is valid for the current assessment state.",
                    severity=DashboardSeverity.INFO,
                )
            )
        if missing_profile_fields:
            actions.append(
                DashboardAction(
                    action_type=DashboardActionType.COMPLETE_PROFILE,
                    title="Review profile setup",
                    description="See which profile preferences are still missing.",
                    destination_route="/app#profile-summary",
                    priority_reason="Some profile preferences are not yet stored.",
                    severity=DashboardSeverity.INFO,
                )
            )
        actions.append(
            DashboardAction(
                action_type=DashboardActionType.LOG_OUT,
                title="Log out",
                description="End this authenticated session.",
                priority_reason="Logout is always available to the authenticated user.",
                severity=DashboardSeverity.INFO,
            )
        )
        return tuple(actions)
