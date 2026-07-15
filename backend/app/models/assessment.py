from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

type AnswerScalar = str | int | float | bool
type AnswerValue = AnswerScalar | list[str]


class QuestionType(StrEnum):
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    DATE = "date"
    HEIGHT = "height"
    WEIGHT = "weight"
    TIME = "time"
    SLIDER = "slider"


class QuestionCategory(StrEnum):
    PERSONAL_INFORMATION = "personal_information"
    GOALS = "goals"
    LIFESTYLE = "lifestyle"
    MEDICAL = "medical"
    INJURIES = "injuries"
    SLEEP = "sleep"
    STRESS = "stress"
    EXPERIENCE = "experience"
    EQUIPMENT = "equipment"
    NUTRITION = "nutrition"
    RECOVERY = "recovery"
    SPORTS = "sports"
    FOOTBALL = "football"
    GOALKEEPER = "goalkeeper"


class VisibilityOperator(StrEnum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    IN = "in"
    CONTAINS = "contains"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"


class QuestionOption(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=200)


class VisibilityRule(BaseModel):
    model_config = ConfigDict(frozen=True)

    question_id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
    operator: VisibilityOperator = VisibilityOperator.EQUALS
    value: AnswerValue


class QuestionPriorityRule(BaseModel):
    model_config = ConfigDict(frozen=True)

    condition: VisibilityRule
    priority_delta: int = Field(ge=-1000, le=1000)


class QuestionValidationRule(BaseModel):
    model_config = ConfigDict(frozen=True)

    min_length: int | None = Field(default=None, ge=0)
    max_length: int | None = Field(default=None, ge=1)
    pattern: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_length_bounds(self) -> "QuestionValidationRule":
        if (
            self.min_length is not None
            and self.max_length is not None
            and self.min_length > self.max_length
        ):
            raise ValueError("min_length cannot exceed max_length.")
        return self


class AssessmentQuestion(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
    category: QuestionCategory
    title: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=1000)
    type: QuestionType
    required: bool = False
    placeholder: str | None = Field(default=None, max_length=300)
    min: float | None = None
    max: float | None = None
    unit: str | None = Field(default=None, max_length=50)
    options: tuple[QuestionOption, ...] = ()
    depends_on: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_]*$")
    visibility_rule: VisibilityRule | None = None
    visibility_rules: tuple[VisibilityRule, ...] = ()
    priority_rules: tuple[QuestionPriorityRule, ...] = ()
    validation_rule: QuestionValidationRule | None = None
    display_order: int = Field(ge=0)
    version: int = Field(ge=1)
    active: bool = True

    @model_validator(mode="after")
    def validate_metadata(self) -> "AssessmentQuestion":
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("min cannot exceed max.")
        choice_types = {QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE}
        if self.type in choice_types and not self.options:
            raise ValueError("Choice questions require options.")
        option_values = [option.value for option in self.options]
        if len(option_values) != len(set(option_values)):
            raise ValueError("Question option values must be unique.")
        if self.visibility_rule and self.depends_on != self.visibility_rule.question_id:
            raise ValueError("depends_on must match the visibility rule question.")
        return self


class SafetyStatus(StrEnum):
    SAFE = "safe"
    CAUTION = "caution"
    STOP = "stop"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: SafetyStatus
    risk_level: RiskLevel
    explanations: tuple[str, ...] = ()
    triggered_rule_ids: tuple[str, ...] = ()


class AssessmentProgress(BaseModel):
    model_config = ConfigDict(frozen=True)

    assessment_completeness: int = Field(ge=0, le=100)
    readiness_score: int = Field(ge=0, le=100)
    missing_categories: tuple[QuestionCategory, ...] = ()
    safety: SafetyEvaluation


class AssessmentSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    goals: tuple[str, ...] = ()
    lifestyle: tuple[str, ...] = ()
    medical_considerations: tuple[str, ...] = ()
    training_readiness: str = "Assessment data is not available."
    equipment: tuple[str, ...] = ()
    experience: str | None = None


class AssessmentStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Assessment(BaseModel):
    """Common identity and audit fields for a user-owned assessment aggregate."""

    model_config = ConfigDict(frozen=True)

    id: str
    user_id: str
    assessment_version: int = Field(ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AssessmentAnswer(BaseModel):
    model_config = ConfigDict(frozen=True)

    question_id: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
    value: AnswerValue
    answered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AssessmentSession(Assessment):
    status: AssessmentStatus = AssessmentStatus.IN_PROGRESS
    answers: dict[str, AssessmentAnswer] = Field(default_factory=dict)
    revision: int = Field(default=0, ge=0)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_activity_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    result_id: str | None = None


class AssessmentResult(Assessment):
    session_id: str
    profile: dict[str, dict[str, AnswerValue]]
    answered_question_ids: tuple[str, ...]
    completed_categories: tuple[QuestionCategory, ...]
    completion_percentage: int = Field(default=100, ge=0, le=100)
    assessment_completeness: int = Field(default=100, ge=0, le=100)
    readiness_score: int = Field(default=100, ge=0, le=100)
    missing_categories: tuple[QuestionCategory, ...] = ()
    safety_status: SafetyStatus = SafetyStatus.SAFE
    risk_level: RiskLevel = RiskLevel.LOW
    safety_explanations: tuple[str, ...] = ()
    summary: AssessmentSummary = Field(default_factory=AssessmentSummary)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
