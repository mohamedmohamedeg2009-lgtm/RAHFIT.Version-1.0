from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

WORKOUT_SESSION_INDEX = "workout_sessions_active_lookup"
WORKOUT_SESSION_FILTER = {"status": "in_progress"}


async def ensure_workout_session_index(collection: Any) -> None:
    """Upgrade the pre-Sprint 3.4 non-unique index without touching documents."""
    indexes = await collection.index_information()
    existing = indexes.get(WORKOUT_SESSION_INDEX)
    if existing and (
        existing.get("unique") is not True
        or existing.get("partialFilterExpression") != WORKOUT_SESSION_FILTER
    ):
        await collection.drop_index(WORKOUT_SESSION_INDEX)
    await collection.create_index(
        [("user_id", 1), ("plan_id", 1), ("workout_day_id", 1), ("status", 1)],
        unique=True,
        partialFilterExpression=WORKOUT_SESSION_FILTER,
        name=WORKOUT_SESSION_INDEX,
    )


async def initialize_indexes(database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    """Register indexes required by implemented domains."""
    await database["users"].create_index("email", unique=True, name="users_email_unique")
    await database["assessment_questions"].create_index(
        [("version", 1), ("question_id", 1)],
        unique=True,
        name="assessment_questions_version_question_unique",
    )
    await database["assessment_questions"].create_index(
        [("version", 1), ("active", 1), ("display_order", 1)],
        name="assessment_questions_active_order",
    )
    await database["assessment_sessions"].create_index(
        [("user_id", 1), ("status", 1)],
        unique=True,
        partialFilterExpression={"status": "in_progress"},
        name="assessment_sessions_one_active_per_user",
    )
    await database["assessment_sessions"].create_index(
        [("user_id", 1), ("updated_at", -1)],
        name="assessment_sessions_user_updated",
    )
    await database["assessment_results"].create_index(
        "session_id", unique=True, name="assessment_results_session_unique"
    )
    await database["nutrition_plans"].create_index(
        [("user_id", 1), ("status", 1)],
        unique=True,
        partialFilterExpression={"status": "active"},
        name="nutrition_plans_one_active_per_user",
    )
    await database["nutrition_plans"].create_index(
        [("user_id", 1), ("generated_at", -1)], name="nutrition_plans_user_history"
    )
    await database["nutrition_daily_logs"].create_index(
        [("user_id", 1), ("date", 1)], unique=True, name="nutrition_logs_user_date_unique"
    )
    await database["workout_plans"].create_index(
        [("user_id", 1), ("status", 1)],
        unique=True,
        partialFilterExpression={"status": "active"},
        name="workout_plans_one_active_per_user",
    )
    await database["workout_plans"].create_index(
        [("user_id", 1), ("generated_at", -1)],
        name="workout_plans_user_history",
    )
    await ensure_workout_session_index(database["workout_sessions"])
    await database["workout_sessions"].create_index(
        [("user_id", 1), ("started_at", -1)],
        name="workout_sessions_user_history",
    )
    await database["assessment_results"].create_index(
        [("user_id", 1), ("generated_at", -1)],
        name="assessment_results_user_latest",
    )
