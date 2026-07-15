from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


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
    await database["assessment_results"].create_index(
        [("user_id", 1), ("generated_at", -1)],
        name="assessment_results_user_latest",
    )
