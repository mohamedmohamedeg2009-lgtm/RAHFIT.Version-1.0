from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.profile.models import UserProfile
from app.readiness.models import ReadinessStatus
from app.workouts.models import SessionStatus, WorkoutSession


class AdaptationAction(StrEnum):
    REDUCE_VOLUME = "reduce_volume"
    REDUCE_INTENSITY = "reduce_intensity"
    REPLACE_EXERCISE = "replace_exercise"
    ADD_RECOVERY_DAY = "add_recovery_day"
    SHORTEN_SESSION = "shorten_session"
    MAINTAIN_PLAN = "maintain_plan"
    REQUIRE_REVIEW = "require_review"
    BLOCK_TRAINING = "block_training"


class AdaptationSeverity(StrEnum):
    INFO = "info"
    CAUTION = "caution"
    HIGH = "high"
    CRITICAL = "critical"


class WorkoutAdaptationRecommendation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    recommendation_code: str = Field(pattern=r"^[a-z][a-z0-9_.]*$")
    action: AdaptationAction
    reason_code: str = Field(pattern=r"^[a-z][a-z0-9_.]*$")
    severity: AdaptationSeverity
    evidence_summary: tuple[str, ...] = Field(min_length=1, max_length=5)
    automatic_application_allowed: bool = False
    affected_exercise_id: str | None = None
    affected_day_number: int | None = Field(default=None, ge=1, le=7)


# Compatibility name for the initial internal draft.
AdaptationRecommendation = WorkoutAdaptationRecommendation


class WorkoutAdaptationEngine:
    """Deterministic, auditable analysis that never mutates a plan."""

    def evaluate(
        self,
        sessions: tuple[WorkoutSession, ...],
        profile: UserProfile,
        readiness_history: tuple[ReadinessStatus, ...] = (),
    ) -> WorkoutAdaptationRecommendation:
        recent = sessions[:5]
        pain_exercise = next(
            (
                exercise
                for session in recent
                for exercise in session.completed_exercises
                if exercise.pain_reported
            ),
            None,
        )
        if pain_exercise is not None:
            return self._recommendation(
                AdaptationAction.BLOCK_TRAINING,
                "adaptation.block_for_pain",
                "session.pain_reported",
                AdaptationSeverity.CRITICAL,
                ("Pain was reported during a recent workout session.",),
                affected_exercise_id=pain_exercise.exercise_id,
            )
        if any(status == ReadinessStatus.BLOCKED for status in readiness_history[:3]):
            return self._recommendation(
                AdaptationAction.BLOCK_TRAINING,
                "adaptation.block_for_readiness",
                "readiness.blocked",
                AdaptationSeverity.CRITICAL,
                ("A recent readiness decision blocked training.",),
            )
        if sum(status == ReadinessStatus.CAUTION for status in readiness_history[:3]) >= 2:
            return self._recommendation(
                AdaptationAction.REQUIRE_REVIEW,
                "adaptation.review_low_readiness",
                "readiness.repeated_caution",
                AdaptationSeverity.HIGH,
                ("Repeated caution readiness decisions require review.",),
            )

        exertion = [
            completed_set.perceived_exertion
            for session in recent
            for exercise in session.completed_exercises
            for completed_set in exercise.completed_sets
            if completed_set.perceived_exertion is not None
        ]
        if sum(value >= 9 for value in exertion) >= 2:
            return self._recommendation(
                AdaptationAction.REDUCE_INTENSITY,
                "adaptation.reduce_intensity",
                "session.repeated_high_exertion",
                AdaptationSeverity.HIGH,
                ("High perceived exertion occurred repeatedly.",),
            )
        if sum(session.completion_percentage < 50 for session in recent) >= 2:
            return self._recommendation(
                AdaptationAction.REDUCE_VOLUME,
                "adaptation.reduce_volume",
                "session.repeated_low_completion",
                AdaptationSeverity.CAUTION,
                ("Less than half of the planned work was completed repeatedly.",),
            )
        if sum(session.status == SessionStatus.ABANDONED for session in recent) >= 2:
            return self._recommendation(
                AdaptationAction.ADD_RECOVERY_DAY,
                "adaptation.add_recovery",
                "session.repeated_abandonment",
                AdaptationSeverity.CAUTION,
                ("Multiple recent sessions were abandoned.",),
            )
        if (
            sum(
                session.actual_duration_minutes is not None
                and session.actual_duration_minutes > session.planned_duration_minutes * 1.25
                for session in recent
            )
            >= 2
        ):
            return self._recommendation(
                AdaptationAction.SHORTEN_SESSION,
                "adaptation.shorten_session",
                "session.repeated_duration_overrun",
                AdaptationSeverity.CAUTION,
                ("Actual duration repeatedly exceeded the planned duration.",),
            )
        skipped: dict[str, int] = {}
        for session in recent:
            for exercise_id in session.skipped_exercise_ids:
                skipped[exercise_id] = skipped.get(exercise_id, 0) + 1
        repeated_skip = next((key for key, count in sorted(skipped.items()) if count >= 2), None)
        if repeated_skip is not None:
            return self._recommendation(
                AdaptationAction.REPLACE_EXERCISE,
                "adaptation.replace_exercise",
                "session.exercise_repeatedly_skipped",
                AdaptationSeverity.CAUTION,
                ("The same approved exercise was skipped repeatedly.",),
                affected_exercise_id=repeated_skip,
            )
        if profile.lifestyle.sleep_hours < 5:
            return self._recommendation(
                AdaptationAction.ADD_RECOVERY_DAY,
                "adaptation.add_recovery",
                "profile.low_sleep",
                AdaptationSeverity.CAUTION,
                ("Reported sleep is below the recovery threshold.",),
            )
        return self._recommendation(
            AdaptationAction.MAINTAIN_PLAN,
            "adaptation.maintain_plan",
            "progress.stable",
            AdaptationSeverity.INFO,
            ("Recent completion and exertion signals are within current limits.",),
            automatic=True,
        )

    @staticmethod
    def _recommendation(
        action: AdaptationAction,
        recommendation_code: str,
        reason_code: str,
        severity: AdaptationSeverity,
        evidence: tuple[str, ...],
        *,
        automatic: bool = False,
        affected_exercise_id: str | None = None,
    ) -> WorkoutAdaptationRecommendation:
        return WorkoutAdaptationRecommendation(
            recommendation_code=recommendation_code,
            action=action,
            reason_code=reason_code,
            severity=severity,
            evidence_summary=evidence,
            automatic_application_allowed=automatic,
            affected_exercise_id=affected_exercise_id,
        )
