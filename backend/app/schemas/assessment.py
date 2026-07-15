from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.models.assessment import (
    AnswerValue,
    AssessmentAnswer,
    AssessmentProgress,
    AssessmentQuestion,
    AssessmentResult,
    AssessmentSession,
    AssessmentStatus,
    AssessmentSummary,
    QuestionCategory,
    QuestionOption,
    QuestionPriorityRule,
    QuestionType,
    QuestionValidationRule,
    RiskLevel,
    SafetyStatus,
    VisibilityRule,
)


class StartAssessmentRequest(BaseModel):
    version: int | None = Field(default=None, ge=1)


class SaveAnswerRequest(BaseModel):
    question_id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
    value: AnswerValue


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: QuestionCategory
    title: str
    description: str | None
    type: QuestionType
    required: bool
    placeholder: str | None
    min: float | None
    max: float | None
    unit: str | None
    options: tuple[QuestionOption, ...]
    depends_on: str | None
    visibility_rule: VisibilityRule | None
    visibility_rules: tuple[VisibilityRule, ...]
    priority_rules: tuple[QuestionPriorityRule, ...]
    validation_rule: QuestionValidationRule | None
    display_order: int
    version: int
    active: bool


class AssessmentSessionResponse(BaseModel):
    id: str
    assessment_version: int
    status: AssessmentStatus
    answers: tuple[AssessmentAnswer, ...]
    revision: int
    started_at: datetime
    last_activity_at: datetime
    completed_at: datetime | None
    result_id: str | None
    progress: AssessmentProgress
    next_question: QuestionResponse | None = None


class SaveAnswerResponse(BaseModel):
    session: AssessmentSessionResponse
    next_question: QuestionResponse | None


class AssessmentResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    assessment_version: int
    profile: dict[str, dict[str, AnswerValue]]
    answered_question_ids: tuple[str, ...]
    completed_categories: tuple[QuestionCategory, ...]
    completion_percentage: int
    assessment_completeness: int
    readiness_score: int
    missing_categories: tuple[QuestionCategory, ...]
    safety_status: SafetyStatus
    risk_level: RiskLevel
    safety_explanations: tuple[str, ...]
    summary: AssessmentSummary
    generated_at: datetime


def question_response(question: AssessmentQuestion | None) -> QuestionResponse | None:
    return QuestionResponse.model_validate(question) if question else None


def session_response(
    session: AssessmentSession,
    progress: AssessmentProgress,
    next_question: AssessmentQuestion | None = None,
) -> AssessmentSessionResponse:
    return AssessmentSessionResponse(
        id=session.id,
        assessment_version=session.assessment_version,
        status=session.status,
        answers=tuple(session.answers.values()),
        revision=session.revision,
        started_at=session.started_at,
        last_activity_at=session.last_activity_at,
        completed_at=session.completed_at,
        result_id=session.result_id,
        progress=progress,
        next_question=question_response(next_question),
    )


def result_response(result: AssessmentResult) -> AssessmentResultResponse:
    return AssessmentResultResponse.model_validate(result)
