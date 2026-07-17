import hashlib
import json
from datetime import date, timedelta
from typing import Any
from uuid import uuid4

import structlog

from app.ai.decision_rules import (
    calculate_data_quality_score,
    calculate_decision_confidence,
    calculate_fatigue_score,
    calculate_injury_risk_score,
    calculate_nutrition_adherence_score,
    calculate_overall_health_score,
    calculate_progress_score,
    calculate_readiness_score,
    calculate_recovery_score,
    calculate_workout_adherence_score,
)
from app.ai.safety_rulesets import CHRONIC_CONDITION_PROTOCOLS, EXERCISE_SUBSTITUTIONS
from app.health import HealthProfileRepository
from app.health.models import HealthProfile
from app.models.ai_decision import (
    DailyDecision,
    DecisionFinding,
    DecisionMetadata,
    DecisionReason,
    DecisionStatus,
    DecisionTrace,
    DecisionWarning,
    InjuryDecision,
    NutritionDecision,
    RecoveryDecision,
    TrainingDecision,
)
from app.models.nutrition import NutritionProgress
from app.models.user import User
from app.models.workout import TrainingGoal
from app.profile import UserProfileRepository
from app.profile.models import UserProfile
from app.readiness.checker import ReadinessChecker
from app.readiness.models import ReadinessStatus
from app.repositories.ai_decisions import AIDecisionRepository
from app.repositories.nutrition import NutritionRepository
from app.users.models import UserIntelligenceSnapshot
from app.workouts.models import WorkoutPlan
from app.workouts.repository import MongoWorkoutRepository

logger = structlog.get_logger("app.services.ai_decision")


class AIDecisionEngineService:
    """Orchestrates deterministic daily decisions, adaptation limits, and explains logic."""

    def __init__(
        self,
        decision_repo: AIDecisionRepository,
        profile_repo: UserProfileRepository,
        health_repo: HealthProfileRepository,
        workout_repo: MongoWorkoutRepository,
        nutrition_repo: NutritionRepository,
    ) -> None:
        self.decision_repo = decision_repo
        self.profile_repo = profile_repo
        self.health_repo = health_repo
        self.workout_repo = workout_repo
        self.nutrition_repo = nutrition_repo
        self.readiness_checker = ReadinessChecker()

    async def get_or_generate_decision(
        self, user: User, effective_date: date, force_regenerate: bool = False
    ) -> DailyDecision:
        """
        Retrieves today's active decision or generates a new one. Enforces idempotency.
        """
        # Fetch snapshots
        profile = await self.profile_repo.get_by_user_id(user.id)
        health_profile = await self.health_repo.get_by_user_id(user.id)
        active_plan = await self.workout_repo.get_active_plan(user.id)

        # Get recent logs
        sessions = await self.workout_repo.list_sessions(user.id, limit=5)

        nutrition_logs = []
        for i in range(3):
            log_date = effective_date - timedelta(days=i + 1)
            prog = await self.nutrition_repo.get_progress(user.id, log_date)
            nutrition_logs.append(prog)

        # Hash input snapshot for idempotency
        input_hash = self._calculate_snapshot_hash(
            profile, health_profile, active_plan, sessions, nutrition_logs
        )

        if not force_regenerate:
            existing = await self.decision_repo.find_active_by_date(user.id, effective_date)
            if existing and existing.input_snapshot_hash == input_hash:
                logger.info("decision_cache_hit", user_id=user.id, effective_date=effective_date)
                return existing

        # Check for completeness of profile and health check
        missing_inputs = []
        if not profile:
            missing_inputs.append("profile")
        if not health_profile:
            missing_inputs.append("health_profile")

        if missing_inputs:
            meta = DecisionMetadata(
                effective_date=effective_date,
                data_quality_score=0,
                confidence_score=10,
                missing_inputs=tuple(missing_inputs),
            )
            decision = self._build_needs_info_decision(
                user.id, effective_date, meta, input_hash, missing_inputs
            )
            await self.decision_repo.supersede_previous_decisions(
                user.id, effective_date, decision.id
            )
            await self.decision_repo.save(decision)
            return decision

        assert profile is not None
        assert health_profile is not None

        # Generate new decision
        decision = await self._generate(
            user.id,
            effective_date,
            profile,
            health_profile,
            active_plan,
            sessions,
            nutrition_logs,
            input_hash,
        )

        # Save to database
        await self.decision_repo.supersede_previous_decisions(user.id, effective_date, decision.id)
        await self.decision_repo.save(decision)
        logger.info(
            "decision_generated",
            user_id=user.id,
            effective_date=effective_date,
            status=decision.status,
        )
        return decision

    async def _generate(
        self,
        user_id: str,
        effective_date: date,
        profile: UserProfile,
        health_profile: HealthProfile,
        active_plan: WorkoutPlan | None,
        sessions: tuple[Any, ...],
        nutrition_logs: list[NutritionProgress],
        input_hash: str,
    ) -> DailyDecision:
        trace_logs = []
        findings = []
        warnings = []
        reason_codes = []

        def add_trace(rule_name: str, condition_met: bool, action: str) -> None:
            trace_logs.append(
                DecisionTrace(rule_name=rule_name, condition_met=condition_met, action_taken=action)
            )

        # Readiness check using standard checker
        snapshot = UserIntelligenceSnapshot(
            user_id=user_id, profile=profile, health_profile=health_profile
        )
        readiness_result = self.readiness_checker.check(snapshot)

        # Expose readiness status to tracing
        is_blocked = readiness_result.status == ReadinessStatus.BLOCKED

        # Calculate scores
        # 1. Readiness Score
        sleep_hours = profile.lifestyle.sleep_hours
        stress_level = profile.lifestyle.stress_level

        # Calculate recent workout session completions
        session_completions = [
            s.completion_percentage for s in sessions if hasattr(s, "completion_percentage")
        ]
        last_adherence = session_completions[0] if session_completions else 100.0

        readiness = calculate_readiness_score(
            sleep_hours=sleep_hours,
            stress_level=stress_level,
            fatigue_level=profile.lifestyle.stress_level,  # proxy subjective fatigue for profile
            soreness_level=3,  # baseline soreness
            last_workout_adherence=last_adherence,
        )

        # 2. Recovery Score
        recovery = calculate_recovery_score(
            sleep_hours=sleep_hours,
            sleep_quality=7,  # baseline quality
            fatigue=4,
            soreness=3,
            stress=stress_level,
        )

        # 3. Nutrition Adherence
        nut_adherence = 100
        if nutrition_logs and active_plan:
            # Check latest log
            latest_log = nutrition_logs[0]
            # Use active plan nutrition target if available, or static defaults
            target_cal = 2000
            target_prot = 150.0
            nut_adherence = calculate_nutrition_adherence_score(
                target_calories=target_cal,
                actual_calories=latest_log.calories_consumed,
                target_protein=target_prot,
                actual_protein=latest_log.protein_consumed,
            )

        # 4. Workout Adherence
        work_adherence = calculate_workout_adherence_score(session_completions[:3])

        # 5. Injury Risk
        active_pain = {}
        for p in health_profile.pain_areas:
            active_pain[p.area] = p.intensity

        active_injuries = []
        for inj in health_profile.injuries:
            active_injuries.append(
                {"active": inj.active, "medically_cleared": inj.medically_cleared}
            )

        injury_risk = calculate_injury_risk_score(
            active_pain_areas=active_pain,
            active_injuries=active_injuries,
            mobility_limitations=len(health_profile.mobility_limitations),
        )

        # 6. Fatigue
        fatigue = calculate_fatigue_score(
            subjective_fatigue=5, sleep_hours=sleep_hours, stress_level=stress_level
        )

        # 7. Progress
        progress = calculate_progress_score(
            weight_trend_pct=0.0, primary_goal=profile.goals.primary_goal.value
        )

        # 8. Overall Health
        overall_health = calculate_overall_health_score(
            readiness=readiness,
            recovery=recovery,
            nutrition_adherence=nut_adherence,
            workout_adherence=work_adherence,
            injury_risk=injury_risk,
        )

        # 9. Data Quality
        findings.append(
            DecisionFinding(
                category="readiness",
                code="fatigue_score",
                message=f"Calculated fatigue score: {fatigue}",
                severity="info",
            )
        )
        findings.append(
            DecisionFinding(
                category="readiness",
                code="progress_score",
                message=f"Calculated progress score: {progress}",
                severity="info",
            )
        )
        findings.append(
            DecisionFinding(
                category="health",
                code="overall_health",
                message=f"Calculated overall health: {overall_health}",
                severity="info",
            )
        )
        profile_complete_pct = readiness_result.completeness_score
        data_quality = calculate_data_quality_score(
            profile_complete_pct=profile_complete_pct,
            has_workout_log=len(sessions) > 0,
            has_nutrition_log=len(nutrition_logs) > 0,
            subjective_recovery_present=True,
        )

        # 10. Confidence
        confidence = calculate_decision_confidence(
            data_quality=data_quality,
            readiness_score=readiness,
            active_injury_present=any(inj.active for inj in health_profile.injuries),
        )

        # --- RULE EVALUATION & DECISION PRECEDENCE ---
        status = DecisionStatus.APPROVED
        approved_actions: list[str] = []
        blocked_actions: list[str] = []
        modifications: list[str] = []

        # Training decision fields
        t_action = "continue_plan"
        t_multiplier_vol = 1.0
        t_multiplier_int = 1.0
        t_notes = "Continue with your normal training schedule."
        t_exercises: tuple[str, ...] = ()

        # Nutrition decision fields
        n_action = "keep_targets"
        n_cal_adj = 0
        n_prot_adj = 0
        n_explanation = "Nutrition targets are currently optimal."

        # Recovery decision fields
        r_guidance = "normal_recovery"
        r_hydration = False
        r_mobility = False
        r_stress = False

        # Injury decision fields
        i_blocked: list[str] = []
        i_active_pain = [p.area for p in health_profile.pain_areas if p.intensity >= 5]
        i_med_clearance = health_profile.requires_medical_clearance

        # Check URGENT SYMPTOMS (Emergency Refusal)
        urgent_symptoms_triggered = False
        # If user has fainted or felling chest pain, or pain >= 8
        for p in health_profile.pain_areas:
            if p.intensity >= 8:
                urgent_symptoms_triggered = True
                findings.append(
                    DecisionFinding(
                        category="safety",
                        code="severe_pain_reported",
                        message=f"Severe pain of {p.intensity}/10 reported in {p.area}",
                        severity="critical",
                    )
                )

        if health_profile.requires_medical_clearance:
            findings.append(
                DecisionFinding(
                    category="safety",
                    code="medical_clearance_required",
                    message="Health profile indicates professional clearance is required.",
                    severity="critical",
                )
            )

        # Precedence Cascade
        # Rule 1: Emergency / Severe Risk Refusal
        if urgent_symptoms_triggered:
            status = DecisionStatus.BLOCKED
            t_action = "block_training"
            t_multiplier_vol = 0.0
            t_multiplier_int = 0.0
            t_notes = "Refuse training. Seek immediate medical attention or professional guidance."
            n_action = "keep_targets"
            r_guidance = "full_rest"
            blocked_actions.append("workout")
            blocked_actions.append("nutrition_deficit")
            reason_codes.append(
                DecisionReason(
                    code="safety.urgent_symptoms",
                    message_en="Urgent physical symptoms detected. Exercise is strictly blocked.",
                    message_ar="تم اكتشاف أعراض جسدية حرجة. يمنع التمرين تماماً.",
                )
            )
            add_trace("emergency_symptoms_check", True, "block_all_training")

        # Rule 2: Medical clearance requirement
        elif health_profile.requires_medical_clearance or is_blocked:
            status = DecisionStatus.BLOCKED
            t_action = "block_training"
            t_multiplier_vol = 0.0
            t_multiplier_int = 0.0
            t_notes = "Planning is paused. Medical clearance from a professional is required."
            blocked_actions.append("workout")
            reason_codes.append(
                DecisionReason(
                    code="safety.medical_clearance_required",
                    message_en="Medical clearance is required before training.",
                    message_ar="مطلوب فحص طبي معتمد قبل البدء بالتمرين.",
                )
            )
            add_trace("medical_clearance_check", True, "block_planning_until_clearance")

        # Rule 3: Injury related blocking
        elif len(health_profile.injuries) > 0 or len(health_profile.mobility_limitations) > 0:
            status = DecisionStatus.RESTRICTED
            t_action = "replace_exercise"
            modifications.append("exclude_affected_movement_patterns")

            # Exclude patterns based on pain/injuries
            excluded_muscle_groups = []
            rehab_notes_en = []
            rehab_notes_ar = []
            for inj in health_profile.injuries:
                if inj.active:
                    excluded_muscle_groups.append(inj.area)
                    i_blocked.append(inj.area)
                    if inj.area in EXERCISE_SUBSTITUTIONS:
                        for sub in EXERCISE_SUBSTITUTIONS[inj.area]:
                            rehab_notes_en.append(
                                f"Replace {sub['original_pattern']} with {sub['safe_alternative']}. Rationale: {sub['rationale_en']}"
                            )
                            rehab_notes_ar.append(
                                f"استبدل {sub['original_pattern']} بـ {sub['safe_alternative']}. السبب: {sub['rationale_ar']}"
                            )

            t_exercises = tuple(excluded_muscle_groups)
            t_notes = f"Excluding exercise movements involving: {', '.join(excluded_muscle_groups)} due to active injury."
            if rehab_notes_en:
                t_notes += " Substitutions prescribed:\n- " + "\n- ".join(rehab_notes_en)
            reason_codes.append(
                DecisionReason(
                    code="injury.exercise_exclusion",
                    message_en="Active injury detected. Affected exercises restricted.",
                    message_ar="تم اكتشاف إصابة نشطة. تم تقييد التمارين المرتبطة بها.",
                )
            )
            add_trace("injury_check", True, "restrict_affected_movement_patterns")

        # Rule 3.5: Chronic Medical Condition check
        if status != DecisionStatus.BLOCKED:
            for cond in health_profile.chronic_conditions:
                cond_name = cond.name.lower()
                if cond_name in CHRONIC_CONDITION_PROTOCOLS:
                    protocol = CHRONIC_CONDITION_PROTOCOLS[cond_name]
                    t_multiplier_int = min(t_multiplier_int, protocol["max_intensity_rpe"] / 10.0)
                    warnings.append(
                        DecisionWarning(
                            code=f"medical.{cond_name}",
                            message_en=protocol["warning_en"],
                            message_ar=protocol["warning_ar"],
                        )
                    )
                    reason_codes.append(
                        DecisionReason(
                            code=f"medical.{cond_name}",
                            message_en=f"Chronic condition protocol applied for {protocol['condition_name']}.",
                            message_ar=f"تم تطبيق بروتوكول الحالة المزمنة لـ {protocol['condition_name']}.",
                        )
                    )
                    add_trace(
                        f"chronic_condition_{cond_name}", True, "restrict_rpe_and_add_warning"
                    )

        # Rule 4: Recovery/Rest threshold
        if status != DecisionStatus.BLOCKED and readiness < 40:
            status = DecisionStatus.RESTRICTED
            t_action = "full_rest"
            t_multiplier_vol = 0.0
            t_multiplier_int = 0.0
            t_notes = "Readiness score is critically low. Rest is prescribed today."
            r_guidance = "full_rest"
            r_hydration = True
            blocked_actions.append("high_intensity_workout")
            reason_codes.append(
                DecisionReason(
                    code="readiness.critical_low",
                    message_en="Readiness is critically low. Full rest is recommended.",
                    message_ar="جاهزية الجسم منخفضة للغاية. ينصح براحة تامة اليوم.",
                )
            )
            add_trace("readiness_rest_gate", True, "prescribe_full_rest")

        # Rule 5: Restricted training modification
        elif status != DecisionStatus.BLOCKED and readiness < 60:
            status = DecisionStatus.RESTRICTED
            t_action = "reduce_volume_and_intensity"
            t_multiplier_vol = 0.6
            t_multiplier_int = 0.7
            t_notes = "Readiness indicates accumulated fatigue. Volume and intensity reduced."
            r_guidance = "active_recovery"
            r_mobility = True
            reason_codes.append(
                DecisionReason(
                    code="readiness.low",
                    message_en="Low readiness. Reducing volume and intensity.",
                    message_ar="جاهزية منخفضة. تم تقليل الكثافة وحجم التمرين.",
                )
            )
            add_trace("readiness_restriction_gate", True, "reduce_volume_and_intensity")

        # Rule 6: Nutrition Safety checks (Deficit limits)
        if status != DecisionStatus.BLOCKED and profile.goals.primary_goal == TrainingGoal.FAT_LOSS:
            # If target weight change rate is unrealistic (handled by checker as aggressive_weight_change)
            for issue in readiness_result.issues:
                if issue.code == "goal.aggressive_weight_change":
                    n_action = "adjust_calories"
                    # Set to safe deficit of 500 kcal
                    n_cal_adj = -500
                    n_explanation = "Aggressive weight loss target detected. Calories adjusted to safe 500 kcal deficit."
                    warnings.append(
                        DecisionWarning(
                            code="nutrition.extreme_deficit_risk",
                            message_en="Unsafe caloric deficit requested. Overridden to safe baseline.",
                            message_ar="تم طلب عجز حراري غير آمن. تم التعديل إلى المعدل الآمن.",
                        )
                    )
                    add_trace("nutrition_safety_check", True, "override_calorie_deficit")

        # Rule 7: Low Confidence fallback
        if status not in (DecisionStatus.BLOCKED, DecisionStatus.RESTRICTED) and confidence < 50:
            status = DecisionStatus.RESTRICTED
            t_action = "maintain_plan"
            n_action = "keep_targets"
            t_notes = "Low data quality or missing metrics. Maintaining current safe targets without progression."
            reason_codes.append(
                DecisionReason(
                    code="confidence.low_data",
                    message_en="Low log confidence. Maintaining current targets.",
                    message_ar="جودة البيانات منخفضة. تم تثبيت الأهداف الحالية.",
                )
            )
            add_trace("confidence_fallback_check", True, "maintain_safe_plan")

        # Rule 8: Allowed Adaptive Recommendation (Progression)
        elif status == DecisionStatus.APPROVED and readiness > 80 and work_adherence > 90:
            t_action = "progress_load"
            t_multiplier_vol = 1.05
            t_notes = "High readiness and adherence. Progressing intensity cautiously."
            reason_codes.append(
                DecisionReason(
                    code="adaptation.progress_load",
                    message_en="Ready for cautious progression.",
                    message_ar="مستعد لزيادة الحمل التدريبي بحذر.",
                )
            )
            add_trace("progression_adaptation_check", True, "progress_load_5_percent")

        # Fallback normal
        if not reason_codes:
            reason_codes.append(
                DecisionReason(
                    code="readiness.normal",
                    message_en="Readiness is stable. Continue plan.",
                    message_ar="الجاهزية مستقرة. استمر في الخطة.",
                )
            )
            add_trace("default_continuation", True, "continue_plan")

        # Map english and arabic overall explanations
        explanation_en, explanation_ar = self._build_explanations(
            status, t_action, n_action, r_guidance
        )

        # Assemble entities
        training_dec = TrainingDecision(
            action=t_action,
            affected_exercises=tuple(t_exercises),
            intensity_multiplier=t_multiplier_int,
            volume_multiplier=t_multiplier_vol,
            reason_codes=tuple(r.code for r in reason_codes),
            safety_justification=t_notes,
            confidence=confidence,
        )

        nutrition_dec = NutritionDecision(
            action=n_action,
            calorie_adjustment=n_cal_adj,
            protein_adjustment_grams=n_prot_adj,
            warnings=tuple(w.code for w in warnings),
            reason_codes=tuple(r.code for r in reason_codes),
            explanation=n_explanation,
        )

        recovery_dec = RecoveryDecision(
            guidance=r_guidance,
            hydration_priority=r_hydration,
            mobility_focus=r_mobility,
            stress_management_prompt=r_stress,
            reassessment_required=is_blocked,
        )

        injury_dec = InjuryDecision(
            blocked_movements=tuple(i_blocked),
            pain_areas_active=tuple(i_active_pain),
            requires_medical_clearance=i_med_clearance,
            warning_message_en=(
                "Active warning: Please train with conservative limits." if i_active_pain else None
            ),
            warning_message_ar="تنبيه: يرجى التدرب بحدود متحفظة." if i_active_pain else None,
        )

        meta = DecisionMetadata(
            effective_date=effective_date,
            data_quality_score=data_quality,
            confidence_score=confidence,
            missing_inputs=(),
        )

        return DailyDecision(
            id=str(uuid4()),
            user_id=user_id,
            effective_date=effective_date,
            status=status,
            approved_actions=tuple(approved_actions),
            blocked_actions=tuple(blocked_actions),
            modifications=tuple(modifications),
            warnings=tuple(warnings),
            reason_codes=tuple(reason_codes),
            human_readable_explanation_en=explanation_en,
            human_readable_explanation_ar=explanation_ar,
            training=training_dec,
            nutrition=nutrition_dec,
            recovery=recovery_dec,
            injury=injury_dec,
            findings=tuple(findings),
            trace=tuple(trace_logs),
            metadata=meta,
            input_snapshot_hash=input_hash,
        )

    def _calculate_snapshot_hash(
        self,
        profile: UserProfile | None,
        health: HealthProfile | None,
        plan: WorkoutPlan | None,
        sessions: tuple[Any, ...],
        logs: list[NutritionProgress],
    ) -> str:
        data = {
            "profile": profile.model_dump(mode="json") if profile else None,
            "health": health.model_dump(mode="json") if health else None,
            "plan_id": plan.plan_id if plan else None,
            "sessions": [s.session_id for s in sessions if hasattr(s, "session_id")],
            "logs": [log.model_dump(mode="json") for log in logs],
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def _build_needs_info_decision(
        self,
        user_id: str,
        effective_date: date,
        meta: DecisionMetadata,
        input_hash: str,
        missing: list[str],
    ) -> DailyDecision:
        missing_str = ", ".join(missing)
        return DailyDecision(
            id=str(uuid4()),
            user_id=user_id,
            effective_date=effective_date,
            status=DecisionStatus.NEEDS_INFO,
            human_readable_explanation_en=f"We need more information before personalization can begin. Missing: {missing_str}",
            human_readable_explanation_ar=f"نحتاج إلى مزيد من المعلومات قبل البدء بالتخصيص. ينقص: {missing_str}",
            training=TrainingDecision(
                action="maintain_plan", safety_justification="Missing metrics", confidence=10
            ),
            nutrition=NutritionDecision(action="keep_targets", explanation="Missing metrics"),
            recovery=RecoveryDecision(guidance="normal_recovery"),
            injury=InjuryDecision(),
            metadata=meta,
            input_snapshot_hash=input_hash,
        )

    def _build_explanations(
        self, status: DecisionStatus, t_action: str, n_action: str, r_guidance: str
    ) -> tuple[str, str]:
        if status == DecisionStatus.BLOCKED:
            return (
                "Your personalized plan is paused due to safety rules. Exercise is not recommended.",
                "تم إيقاف خطتك المخصصة مؤقتاً لدواعي السلامة. لا ينصح بممارسة التمارين حالياً.",
            )
        elif status == DecisionStatus.RESTRICTED:
            msg_en = "Your plan is active but modified to adapt to your current readiness, pain, or recovery signals."
            msg_ar = "خطتك نشطة ولكن تم تعديلها لتتكيف مع جاهزيتك الحالية، أو الألم، أو إشارات الاستشفاء."
            if t_action == "full_rest" or r_guidance == "full_rest":
                msg_en = "Critical recovery indicators detected. A full rest day is prescribed to support recovery."
                msg_ar = "تم رصد مؤشرات استشفاء حرجة. تم تحديد يوم راحة تام لدعم تعافي الجسم."
            return msg_en, msg_ar
        else:
            return (
                "Your health markers and training metrics are optimal. Continue your normal progression.",
                "مؤشراتك الصحية ومقاييسك التدريبية مثالية. استمر في تقدمك الطبيعي.",
            )
