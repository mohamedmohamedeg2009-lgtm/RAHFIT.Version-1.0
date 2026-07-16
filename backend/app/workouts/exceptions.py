class WorkoutError(Exception):
    """Stable, privacy-safe base error for the workout application boundary."""

    reason_code = "workout_error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.reason_code)


class WorkoutProfileIncompleteError(WorkoutError):
    reason_code = "workout_profile_incomplete"


class WorkoutHealthProfileIncompleteError(WorkoutError):
    reason_code = "workout_health_profile_incomplete"


class WorkoutReadinessBlockedError(WorkoutError):
    reason_code = "workout_readiness_blocked"


class WorkoutGenerationError(WorkoutError):
    reason_code = "workout_generation_failed"


class WorkoutValidationError(WorkoutError):
    reason_code = "workout_validation_failed"

    def __init__(self, issues: tuple[str, ...]) -> None:
        super().__init__("; ".join(issues))
        self.issues = issues


class WorkoutPlanNotFoundError(WorkoutError):
    reason_code = "workout_plan_not_found"


class WorkoutSessionNotFoundError(WorkoutError):
    reason_code = "workout_session_not_found"


class WorkoutOwnershipError(WorkoutError):
    reason_code = "workout_owner_mismatch"


class WorkoutExerciseUnavailableError(WorkoutError):
    reason_code = "workout_exercise_unavailable"


class WorkoutActivePlanConflictError(WorkoutError):
    reason_code = "workout_active_plan_conflict"


class WorkoutPlanArchivedError(WorkoutError):
    reason_code = "workout_plan_archived"


class WorkoutSessionStateError(WorkoutError):
    reason_code = "workout_session_state_invalid"


class WorkoutMedicalClearanceRequiredError(WorkoutError):
    reason_code = "workout_medical_clearance_required"


class WorkoutPersistenceError(WorkoutError):
    reason_code = "workout_persistence_failed"

    def __init__(self, *, compensation_succeeded: bool) -> None:
        super().__init__(self.reason_code)
        self.compensation_succeeded = compensation_succeeded


class WorkoutAIEnhancementError(WorkoutError):
    reason_code = "workout_ai_enhancement_failed"


# Compatibility names retained for code written against the initial internal draft.
WorkoutNotReadyError = WorkoutReadinessBlockedError
WorkoutNotFoundError = WorkoutPlanNotFoundError
WorkoutConflictError = WorkoutActivePlanConflictError
