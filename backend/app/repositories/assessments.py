from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.models.assessment import (
    AssessmentAnswer,
    AssessmentQuestion,
    AssessmentResult,
    AssessmentSession,
    AssessmentStatus,
)


class ActiveAssessmentExistsError(Exception):
    """Raised when concurrent requests attempt to create duplicate active sessions."""


class AssessmentRevisionConflictError(Exception):
    """Raised when an assessment session changed during an update."""


class AssessmentRepository:
    """MongoDB persistence boundary for the assessment aggregate."""

    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.database = database
        self.questions = database["assessment_questions"]
        self.sessions = database["assessment_sessions"]
        self.results = database["assessment_results"]

    @staticmethod
    def _to_question(document: dict[str, Any]) -> AssessmentQuestion:
        payload = dict(document)
        payload["id"] = str(payload.pop("question_id"))
        payload.pop("_id", None)
        return AssessmentQuestion.model_validate(payload)

    @staticmethod
    def _to_session(document: dict[str, Any]) -> AssessmentSession:
        payload = dict(document)
        payload["id"] = str(payload.pop("_id"))
        return AssessmentSession.model_validate(payload)

    @staticmethod
    def _to_result(document: dict[str, Any]) -> AssessmentResult:
        payload = dict(document)
        payload["id"] = str(payload.pop("_id"))
        return AssessmentResult.model_validate(payload)

    async def latest_question_version(self) -> int | None:
        document = await self.questions.find_one(
            {"active": True}, sort=[("version", -1)], projection={"version": True}
        )
        return int(document["version"]) if document else None

    async def list_questions(self, version: int) -> list[AssessmentQuestion]:
        cursor = self.questions.find({"version": version, "active": True}).sort("display_order", 1)
        documents = await cursor.to_list(length=None)
        return [self._to_question(document) for document in documents]

    async def find_active_session(self, user_id: str) -> AssessmentSession | None:
        document = await self.sessions.find_one(
            {"user_id": user_id, "status": AssessmentStatus.IN_PROGRESS.value}
        )
        return self._to_session(document) if document else None

    async def create_session(self, user_id: str, version: int) -> AssessmentSession:
        now = datetime.now(UTC)
        document: dict[str, Any] = {
            "user_id": user_id,
            "assessment_version": version,
            "status": AssessmentStatus.IN_PROGRESS.value,
            "answers": {},
            "revision": 0,
            "started_at": now,
            "last_activity_at": now,
            "completed_at": None,
            "result_id": None,
            "created_at": now,
            "updated_at": now,
        }
        try:
            inserted = await self.sessions.insert_one(document)
        except DuplicateKeyError as exc:
            raise ActiveAssessmentExistsError from exc
        document["_id"] = inserted.inserted_id
        return self._to_session(document)

    async def find_session(self, session_id: str, user_id: str) -> AssessmentSession | None:
        if not ObjectId.is_valid(session_id):
            return None
        document = await self.sessions.find_one({"_id": ObjectId(session_id), "user_id": user_id})
        return self._to_session(document) if document else None

    async def save_answer(
        self,
        session: AssessmentSession,
        answer: AssessmentAnswer,
        removed_question_ids: tuple[str, ...],
    ) -> AssessmentSession:
        now = datetime.now(UTC)
        update: dict[str, Any] = {
            "$set": {
                f"answers.{answer.question_id}": answer.model_dump(mode="python"),
                "last_activity_at": now,
                "updated_at": now,
            },
            "$inc": {"revision": 1},
        }
        if removed_question_ids:
            update["$unset"] = {
                f"answers.{question_id}": "" for question_id in removed_question_ids
            }
        document = await self.sessions.find_one_and_update(
            {
                "_id": ObjectId(session.id),
                "user_id": session.user_id,
                "status": AssessmentStatus.IN_PROGRESS.value,
                "revision": session.revision,
            },
            update,
            return_document=ReturnDocument.AFTER,
        )
        if not document:
            raise AssessmentRevisionConflictError
        return self._to_session(document)

    async def complete_session(
        self, session: AssessmentSession, result: AssessmentResult
    ) -> AssessmentSession:
        now = datetime.now(UTC)
        result_document = result.model_dump(mode="python", exclude={"id"})
        result_document["_id"] = result.id

        async with (
            await self.database.client.start_session() as mongo_session,
            mongo_session.start_transaction(),
        ):
            document = await self.sessions.find_one_and_update(
                {
                    "_id": ObjectId(session.id),
                    "user_id": session.user_id,
                    "status": AssessmentStatus.IN_PROGRESS.value,
                    "revision": session.revision,
                },
                {
                    "$set": {
                        "status": AssessmentStatus.COMPLETED.value,
                        "completed_at": now,
                        "result_id": result.id,
                        "last_activity_at": now,
                        "updated_at": now,
                    },
                    "$inc": {"revision": 1},
                },
                return_document=ReturnDocument.AFTER,
                session=mongo_session,
            )
            if not document:
                raise AssessmentRevisionConflictError
            await self.results.insert_one(result_document, session=mongo_session)
        return self._to_session(document)

    async def find_result_by_session(
        self, session_id: str, user_id: str
    ) -> AssessmentResult | None:
        document = await self.results.find_one({"session_id": session_id, "user_id": user_id})
        return self._to_result(document) if document else None

    async def find_latest_result(self, user_id: str) -> AssessmentResult | None:
        document = await self.results.find_one({"user_id": user_id}, sort=[("generated_at", -1)])
        return self._to_result(document) if document else None
