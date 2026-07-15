from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.assessment_catalog import ASSESSMENT_QUESTION_CATALOG


async def initialize_assessment_catalog(
    database: AsyncIOMotorDatabase[dict[str, Any]],
) -> None:
    """Provision built-in catalogue versions without overwriting deployed configuration."""
    collection = database["assessment_questions"]
    for version, questions in ASSESSMENT_QUESTION_CATALOG.versions.items():
        for question in questions:
            document = question.model_dump(mode="python", exclude={"id"})
            document["question_id"] = question.id
            await collection.update_one(
                {"version": version, "question_id": question.id},
                {"$setOnInsert": document},
                upsert=True,
            )
