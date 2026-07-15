import pytest

from app.models.assessment import (
    AssessmentAnswer,
    AssessmentQuestion,
    QuestionCategory,
    QuestionType,
    RiskLevel,
    SafetyStatus,
)
from app.services.assessment_branching import (
    AdaptiveBranchingEngine,
    CatalogConfigurationError,
)
from app.services.assessment_catalog import (
    ASSESSMENT_QUESTION_CATALOG,
    CURRENT_ASSESSMENT_VERSION,
)
from app.services.assessment_readiness import ReadinessCalculator
from app.services.assessment_safety import SafetyRuleEngine
from app.services.assessment_validation import (
    AssessmentConsistencyError,
    AssessmentConsistencyValidator,
)


def answers(**values: str | int | float | bool | list[str]) -> dict[str, AssessmentAnswer]:
    return {
        question_id: AssessmentAnswer(question_id=question_id, value=value)
        for question_id, value in values.items()
    }


def catalog() -> list[AssessmentQuestion]:
    return list(ASSESSMENT_QUESTION_CATALOG.get(CURRENT_ASSESSMENT_VERSION))


def visible_ids(answer_values: dict[str, AssessmentAnswer]) -> list[str]:
    return [
        question.id
        for question in AdaptiveBranchingEngine().visible_questions(catalog(), answer_values)
    ]


def test_catalog_is_versioned_grouped_and_dependency_safe() -> None:
    question_catalog = ASSESSMENT_QUESTION_CATALOG

    assert question_catalog.latest_version == CURRENT_ASSESSMENT_VERSION
    assert QuestionCategory.MEDICAL in question_catalog.grouped(CURRENT_ASSESSMENT_VERSION)
    assert QuestionCategory.NUTRITION in question_catalog.grouped(CURRENT_ASSESSMENT_VERSION)
    assert len({question.id for question in catalog()}) == len(catalog())
    AdaptiveBranchingEngine().validate_catalog(catalog())


def test_catalog_validation_rejects_missing_dependencies_and_cycles() -> None:
    missing_dependency = AssessmentQuestion(
        id="dependent",
        category=QuestionCategory.GOALS,
        title="Dependent",
        type=QuestionType.BOOLEAN,
        depends_on="missing",
        display_order=1,
        version=1,
    )
    with pytest.raises(CatalogConfigurationError):
        AdaptiveBranchingEngine().validate_catalog([missing_dependency])

    first = missing_dependency.model_copy(update={"id": "first", "depends_on": "second"})
    second = missing_dependency.model_copy(update={"id": "second", "depends_on": "first"})
    with pytest.raises(CatalogConfigurationError):
        AdaptiveBranchingEngine().validate_catalog([first, second])


def test_gender_age_and_experience_branches_are_deterministic() -> None:
    male_branch = visible_ids(answers(user_gender="male"))
    non_male_branch = visible_ids(answers(user_gender="female"))

    assert "male_health_context" in male_branch
    assert "male_health_context" not in non_male_branch
    assert "advanced_programming_style" not in visible_ids(answers(age=15, experience="advanced"))
    assert "advanced_programming_style" in visible_ids(answers(age=16, experience="advanced"))
    assert "advanced_programming_style" not in visible_ids(answers(age=30, experience="beginner"))


def test_goal_injury_and_location_answers_change_visibility_and_priority() -> None:
    fat_loss_ids = visible_ids(answers(primary_goal="fat_loss"))
    assert fat_loss_ids.index("nutrition_pattern") < fat_loss_ids.index("has_injury")
    assert "target_weight" in fat_loss_ids

    knee_ids = visible_ids(answers(has_injury=True, injury_area=["knee"]))
    assert "knee_injury_details" in knee_ids
    assert "knee_injury_details" not in visible_ids(answers(has_injury=True, injury_area=["ankle"]))

    home_ids = visible_ids(answers(home_training=True))
    gym_ids = visible_ids(answers(home_training=False))
    assert "equipment_available" in home_ids
    assert "commercial_gym_equipment" not in home_ids
    assert "equipment_available" not in gym_ids
    assert "commercial_gym_equipment" in gym_ids


@pytest.mark.parametrize(
    ("question_id", "expected_risk"),
    [
        ("chest_pain", RiskLevel.CRITICAL),
        ("loss_of_consciousness", RiskLevel.CRITICAL),
        ("medical_red_flags", RiskLevel.CRITICAL),
        ("recent_surgery", RiskLevel.HIGH),
        ("heart_disease", RiskLevel.HIGH),
        ("uncontrolled_hypertension", RiskLevel.HIGH),
        ("severe_dizziness", RiskLevel.HIGH),
        ("serious_injury", RiskLevel.HIGH),
    ],
)
def test_stop_safety_rules_classify_risk(question_id: str, expected_risk: RiskLevel) -> None:
    evaluation = SafetyRuleEngine().evaluate(answers(**{question_id: True}))

    assert evaluation.status == SafetyStatus.STOP
    assert evaluation.risk_level == expected_risk
    assert evaluation.explanations


def test_safety_engine_uses_highest_triggered_risk_and_caution() -> None:
    caution = SafetyRuleEngine().evaluate(answers(pregnancy=True))
    combined = SafetyRuleEngine().evaluate(
        answers(pregnancy=True, chest_pain=True, recent_surgery=True)
    )

    assert caution.status == SafetyStatus.CAUTION
    assert caution.risk_level == RiskLevel.MEDIUM
    assert combined.status == SafetyStatus.STOP
    assert combined.risk_level == RiskLevel.CRITICAL
    assert len(combined.triggered_rule_ids) == 3


def test_readiness_uses_visible_completeness_missing_categories_and_safety() -> None:
    questions = [
        AssessmentQuestion(
            id="goal",
            category=QuestionCategory.GOALS,
            title="Goal",
            type=QuestionType.TEXT,
            required=True,
            display_order=1,
            version=1,
        ),
        AssessmentQuestion(
            id="sleep",
            category=QuestionCategory.SLEEP,
            title="Sleep",
            type=QuestionType.NUMBER,
            required=True,
            display_order=2,
            version=1,
        ),
    ]
    safety_engine = SafetyRuleEngine()
    calculator = ReadinessCalculator()
    safe_progress = calculator.calculate(
        questions, answers(goal="fitness"), safety_engine.evaluate({})
    )
    caution_progress = calculator.calculate(
        questions,
        answers(goal="fitness"),
        safety_engine.evaluate(answers(pregnancy=True)),
    )
    stop_progress = calculator.calculate(
        questions,
        answers(goal="fitness"),
        safety_engine.evaluate(answers(chest_pain=True)),
    )

    assert safe_progress.assessment_completeness == 50
    assert safe_progress.readiness_score == 50
    assert safe_progress.missing_categories == (QuestionCategory.SLEEP,)
    assert caution_progress.readiness_score == 35
    assert stop_progress.readiness_score == 0


@pytest.mark.parametrize(
    "values",
    [
        {"age": 12},
        {"height": 0},
        {"current_weight": -1},
        {"sleep_hours": 25},
        {"equipment_available": ["none", "dumbbells"]},
        {"injury_area": ["none", "knee"]},
        {"primary_goal": "fat_loss", "current_weight": 80, "target_weight": 90},
        {"primary_goal": "muscle_gain", "current_weight": 80, "target_weight": 70},
    ],
)
def test_logical_consistency_rejects_impossible_or_conflicting_answers(
    values: dict[str, str | int | float | bool | list[str]],
) -> None:
    with pytest.raises(AssessmentConsistencyError):
        AssessmentConsistencyValidator().validate(answers(**values))


def test_logical_consistency_accepts_valid_boundary_values() -> None:
    AssessmentConsistencyValidator().validate(
        answers(
            age=13,
            height=80,
            current_weight=80,
            primary_goal="fat_loss",
            target_weight=70,
            sleep_hours=24,
            equipment_available=["none"],
        )
    )
