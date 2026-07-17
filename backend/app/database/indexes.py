from collections.abc import Sequence
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

WORKOUT_SESSION_INDEX = "workout_sessions_active_lookup"
WORKOUT_SESSION_FILTER = {"status": "in_progress"}
AI_CONVERSATION_INDEXES: tuple[tuple[str, tuple[tuple[str, int], ...]], ...] = (
    (
        "ai_conversations_owner_activity",
        (("user_id", 1), ("last_activity_at", -1), ("_id", -1)),
    ),
    ("ai_conversations_owner_status", (("user_id", 1), ("status", 1))),
    ("ai_conversations_created_at", (("created_at", -1),)),
)
AI_MESSAGE_INDEXES: tuple[tuple[str, tuple[tuple[str, int], ...]], ...] = (
    (
        "ai_messages_conversation_chronology",
        (("conversation_id", 1), ("created_at", 1), ("_id", 1)),
    ),
    (
        "ai_messages_owner_conversation",
        (("user_id", 1), ("conversation_id", 1), ("deleted_at", 1)),
    ),
    ("ai_messages_owner_id", (("user_id", 1), ("_id", 1))),
)
USER_INTELLIGENCE_INDEXES: tuple[tuple[str, str], ...] = (
    ("user_profiles", "user_profiles_user_unique"),
    ("health_profiles", "health_profiles_user_unique"),
)
INTELLIGENT_WORKOUT_PLAN_COLLECTION = "intelligent_workout_plans"
INTELLIGENT_WORKOUT_SESSION_COLLECTION = "intelligent_workout_sessions"
INTELLIGENT_WORKOUT_GENERATION_INDEX = "intelligent_workout_plans_generation_history"
INTELLIGENT_WORKOUT_GENERATION_KEYS: tuple[tuple[str, int], ...] = (
    ("user_id", 1),
    ("generation_metadata.generation_key", 1),
    ("version", -1),
)


async def ensure_intelligent_workout_indexes(database: Any) -> None:
    plans = database[INTELLIGENT_WORKOUT_PLAN_COLLECTION]
    sessions = database[INTELLIGENT_WORKOUT_SESSION_COLLECTION]
    await plans.create_index(
        "plan_id",
        unique=True,
        name="intelligent_workout_plans_plan_id_unique",
    )
    await plans.create_index(
        [("user_id", 1), ("status", 1)],
        unique=True,
        partialFilterExpression={"status": "active"},
        name="intelligent_workout_plans_one_active_per_user",
    )
    await plans.create_index(
        [("user_id", 1), ("generated_at", -1)],
        name="intelligent_workout_plans_owner_history",
    )
    await plans.create_index(
        [("user_id", 1), ("status", 1), ("generated_at", -1)],
        name="intelligent_workout_plans_owner_status",
    )
    await ensure_named_index(
        plans,
        INTELLIGENT_WORKOUT_GENERATION_KEYS,
        INTELLIGENT_WORKOUT_GENERATION_INDEX,
    )
    await sessions.create_index(
        "session_id",
        unique=True,
        name="intelligent_workout_sessions_session_id_unique",
    )
    await sessions.create_index(
        [("user_id", 1), ("plan_id", 1), ("started_at", -1)],
        name="intelligent_workout_sessions_owner_plan_history",
    )
    await sessions.create_index(
        [("user_id", 1), ("status", 1), ("started_at", -1)],
        name="intelligent_workout_sessions_owner_status",
    )


async def ensure_named_index(collection: Any, keys: Sequence[tuple[str, int]], name: str) -> None:
    """Create one owned index after safely resolving same-name definition drift."""
    indexes = await collection.index_information()
    existing = indexes.get(name)
    expected_keys = list(keys)
    if existing and existing.get("key") == expected_keys:
        return
    if existing:
        await collection.drop_index(name)
    await collection.create_index(expected_keys, name=name)


async def ensure_ai_conversation_indexes(database: Any) -> None:
    for name, keys in AI_CONVERSATION_INDEXES:
        await ensure_named_index(database["ai_conversations"], keys, name)
    for name, keys in AI_MESSAGE_INDEXES:
        await ensure_named_index(database["ai_messages"], keys, name)


async def ensure_user_intelligence_indexes(database: Any) -> None:
    for collection_name, index_name in USER_INTELLIGENCE_INDEXES:
        await database[collection_name].create_index(
            "user_id",
            unique=True,
            name=index_name,
        )


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
    await ensure_user_intelligence_indexes(database)
    await ensure_intelligent_workout_indexes(database)
    await ensure_ai_conversation_indexes(database)
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
    await database["users"].create_index(
        [("provider", 1), ("provider_subject", 1)],
        unique=True,
        partialFilterExpression={"is_active": True},
        name="users_provider_subject_unique",
    )
    await database["password_reset_tokens"].create_index(
        "token_hash",
        unique=True,
        name="password_reset_tokens_hash_unique",
    )
    await database["password_reset_tokens"].create_index(
        "expires_at",
        expireAfterSeconds=0,
        name="password_reset_tokens_ttl",
    )
