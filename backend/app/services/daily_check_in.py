import uuid
from datetime import UTC, date, datetime

from app.models.daily_check_in import DailyCheckIn
from app.repositories.daily_check_in import MongoDailyCheckInRepository
from app.schemas.daily_check_in import DailyCheckInCreate
from app.services.daily_check_in_engine import DailyCheckInEngine


class DailyCheckInService:
    """Orchestrates daily check-in validation, deterministic scoring, and persistence."""

    def __init__(
        self,
        repository: MongoDailyCheckInRepository,
        engine: DailyCheckInEngine | None = None,
    ) -> None:
        self.repository = repository
        self.engine = engine or DailyCheckInEngine()

    async def submit_check_in(
        self, user_id: str, payload: DailyCheckInCreate
    ) -> DailyCheckIn:
        check_in_date = payload.check_in_date or datetime.now(UTC).date()
        inputs = payload.to_inputs()
        readiness_result = self.engine.calculate(inputs)

        existing = await self.repository.get_by_date(user_id, check_in_date)
        now = datetime.now(UTC)

        if existing:
            check_in = existing.model_copy(
                update={
                    "inputs": inputs,
                    "readiness_result": readiness_result,
                    "updated_at": now,
                }
            )
        else:
            check_in_id = uuid.uuid4().hex
            check_in = DailyCheckIn(
                id=check_in_id,
                user_id=user_id,
                date=check_in_date,
                inputs=inputs,
                readiness_result=readiness_result,
                created_at=now,
                updated_at=now,
            )

        return await self.repository.upsert(check_in)

    async def get_today_check_in(
        self, user_id: str, target_date: date | None = None
    ) -> DailyCheckIn | None:
        check_in_date = target_date or datetime.now(UTC).date()
        return await self.repository.get_by_date(user_id, check_in_date)

    async def list_history(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[list[DailyCheckIn], int]:
        return await self.repository.list_history(user_id, limit, offset)
