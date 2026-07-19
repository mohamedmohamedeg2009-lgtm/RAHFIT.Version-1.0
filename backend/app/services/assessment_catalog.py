from dataclasses import dataclass

from app.models.assessment import (
    AssessmentQuestion,
    QuestionCategory,
    QuestionOption,
    QuestionPriorityRule,
    QuestionType,
    VisibilityOperator,
    VisibilityRule,
)
from app.services.assessment_branching import AdaptiveBranchingEngine

CURRENT_ASSESSMENT_VERSION = 2


def _options(*items: tuple[str, str]) -> tuple[QuestionOption, ...]:
    return tuple(QuestionOption(value=value, label=label) for value, label in items)


def _rule(
    question_id: str,
    value: str | int | float | bool | list[str],
    operator: VisibilityOperator = VisibilityOperator.EQUALS,
) -> VisibilityRule:
    return VisibilityRule(question_id=question_id, operator=operator, value=value)


VERSION_1_QUESTIONS: tuple[AssessmentQuestion, ...] = (
    AssessmentQuestion(
        id="age",
        category=QuestionCategory.PERSONAL_INFORMATION,
        title="What is your age?",
        type=QuestionType.INTEGER,
        required=True,
        min=13,
        max=100,
        unit="years",
        display_order=10,
        version=1,
    ),
    AssessmentQuestion(
        id="user_gender",
        category=QuestionCategory.PERSONAL_INFORMATION,
        title="Which gender option should the assessment use?",
        description="This optional answer is used only for relevant assessment branches.",
        type=QuestionType.SINGLE_CHOICE,
        options=_options(
            ("male", "Male"),
            ("female", "Female"),
            ("another_identity", "Another identity"),
            ("prefer_not_to_say", "Prefer not to say"),
        ),
        display_order=20,
        version=1,
    ),
    AssessmentQuestion(
        id="male_health_context",
        category=QuestionCategory.MEDICAL,
        title="Are there male-specific health considerations that affect exercise?",
        type=QuestionType.BOOLEAN,
        visibility_rules=(_rule("user_gender", "male"),),
        display_order=30,
        version=1,
    ),
    AssessmentQuestion(
        id="height",
        category=QuestionCategory.PERSONAL_INFORMATION,
        title="What is your height?",
        type=QuestionType.HEIGHT,
        required=True,
        min=80,
        max=250,
        unit="cm",
        display_order=40,
        version=1,
    ),
    AssessmentQuestion(
        id="current_weight",
        category=QuestionCategory.PERSONAL_INFORMATION,
        title="What is your current weight?",
        type=QuestionType.WEIGHT,
        required=True,
        min=20,
        max=350,
        unit="kg",
        display_order=50,
        version=1,
    ),
    AssessmentQuestion(
        id="primary_goal",
        category=QuestionCategory.GOALS,
        title="What is your primary goal?",
        type=QuestionType.SINGLE_CHOICE,
        required=True,
        options=_options(
            ("fat_loss", "Fat loss"),
            ("muscle_gain", "Muscle gain"),
            ("general_fitness", "General fitness"),
            ("athletic_performance", "Athletic performance"),
        ),
        display_order=60,
        version=1,
    ),
    AssessmentQuestion(
        id="target_weight",
        category=QuestionCategory.GOALS,
        title="What is your target weight?",
        type=QuestionType.WEIGHT,
        required=True,
        min=20,
        max=350,
        unit="kg",
        visibility_rules=(
            _rule(
                "primary_goal",
                ["fat_loss", "muscle_gain"],
                VisibilityOperator.IN,
            ),
        ),
        display_order=70,
        version=1,
    ),
    AssessmentQuestion(
        id="nutrition_pattern",
        category=QuestionCategory.NUTRITION,
        title="Which eating pattern best describes your routine?",
        type=QuestionType.SINGLE_CHOICE,
        required=True,
        options=_options(
            ("structured", "Structured meals"),
            ("irregular", "Irregular meals"),
            ("frequent_snacking", "Frequent snacking"),
            ("other", "Other"),
        ),
        priority_rules=(
            QuestionPriorityRule(condition=_rule("primary_goal", "fat_loss"), priority_delta=-65),
        ),
        display_order=130,
        version=1,
    ),
    AssessmentQuestion(
        id="has_injury",
        category=QuestionCategory.INJURIES,
        title="Do you currently have an injury or movement limitation?",
        type=QuestionType.BOOLEAN,
        required=True,
        display_order=80,
        version=1,
    ),
    AssessmentQuestion(
        id="injury_area",
        category=QuestionCategory.INJURIES,
        title="Which areas are affected?",
        type=QuestionType.MULTIPLE_CHOICE,
        required=True,
        options=_options(
            ("knee", "Knee"),
            ("ankle", "Ankle"),
            ("back", "Back"),
            ("shoulder", "Shoulder"),
            ("other", "Other"),
        ),
        visibility_rules=(_rule("has_injury", True),),
        display_order=90,
        version=1,
    ),
    AssessmentQuestion(
        id="knee_injury_details",
        category=QuestionCategory.INJURIES,
        title="Describe how the knee injury affects movement.",
        type=QuestionType.TEXTAREA,
        required=True,
        visibility_rules=(_rule("injury_area", "knee", VisibilityOperator.CONTAINS),),
        display_order=100,
        version=1,
    ),
    AssessmentQuestion(
        id="serious_injury",
        category=QuestionCategory.MEDICAL,
        title="Is the reported injury serious or awaiting medical clearance?",
        type=QuestionType.BOOLEAN,
        required=True,
        visibility_rules=(_rule("has_injury", True),),
        display_order=110,
        version=1,
    ),
    AssessmentQuestion(
        id="experience",
        category=QuestionCategory.EXPERIENCE,
        title="What is your training experience?",
        type=QuestionType.SINGLE_CHOICE,
        required=True,
        options=_options(
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ),
        display_order=120,
        version=1,
    ),
    AssessmentQuestion(
        id="advanced_programming_style",
        category=QuestionCategory.EXPERIENCE,
        title="Which advanced programming style do you currently use?",
        type=QuestionType.MULTIPLE_CHOICE,
        options=_options(
            ("periodization", "Periodization"),
            ("velocity_based", "Velocity-based training"),
            ("autoregulation", "Autoregulation"),
        ),
        visibility_rules=(
            _rule("experience", "advanced"),
            _rule("age", 16, VisibilityOperator.GREATER_THAN_OR_EQUAL),
        ),
        display_order=140,
        version=1,
    ),
    AssessmentQuestion(
        id="home_training",
        category=QuestionCategory.LIFESTYLE,
        title="Will most training take place at home?",
        type=QuestionType.BOOLEAN,
        required=True,
        display_order=150,
        version=1,
    ),
    AssessmentQuestion(
        id="equipment_available",
        category=QuestionCategory.EQUIPMENT,
        title="Which home equipment is available?",
        type=QuestionType.MULTIPLE_CHOICE,
        required=True,
        options=_options(
            ("none", "No equipment"),
            ("dumbbells", "Dumbbells"),
            ("bands", "Resistance bands"),
            ("bench", "Bench"),
            ("pull_up_bar", "Pull-up bar"),
        ),
        visibility_rules=(_rule("home_training", True),),
        display_order=160,
        version=1,
    ),
    AssessmentQuestion(
        id="commercial_gym_equipment",
        category=QuestionCategory.EQUIPMENT,
        title="Which commercial gym equipment can you access?",
        type=QuestionType.MULTIPLE_CHOICE,
        required=True,
        options=_options(
            ("free_weights", "Free weights"),
            ("machines", "Resistance machines"),
            ("cardio", "Cardio machines"),
            ("functional_area", "Functional training area"),
        ),
        visibility_rules=(_rule("home_training", False),),
        display_order=170,
        version=1,
    ),
    AssessmentQuestion(
        id="sleep_hours",
        category=QuestionCategory.SLEEP,
        title="How many hours do you usually sleep per night?",
        type=QuestionType.NUMBER,
        required=True,
        min=0,
        max=24,
        unit="hours",
        display_order=180,
        version=1,
    ),
    AssessmentQuestion(
        id="stress_level",
        category=QuestionCategory.STRESS,
        title="How would you rate your current stress?",
        type=QuestionType.SLIDER,
        required=True,
        min=0,
        max=10,
        display_order=190,
        version=1,
    ),
    AssessmentQuestion(
        id="pregnancy",
        category=QuestionCategory.MEDICAL,
        title="Is pregnancy currently relevant to exercise planning?",
        type=QuestionType.BOOLEAN,
        required=True,
        display_order=200,
        version=1,
    ),
    *tuple(
        AssessmentQuestion(
            id=question_id,
            category=QuestionCategory.MEDICAL,
            title=title,
            type=QuestionType.BOOLEAN,
            required=True,
            display_order=display_order,
            version=1,
        )
        for question_id, title, display_order in (
            ("chest_pain", "Do you experience chest pain during activity or at rest?", 210),
            ("recent_surgery", "Have you had recent surgery without clearance?", 220),
            ("heart_disease", "Have you been diagnosed with heart disease?", 230),
            (
                "uncontrolled_hypertension",
                "Do you have uncontrolled high blood pressure?",
                240,
            ),
            ("severe_dizziness", "Do you experience severe unexplained dizziness?", 250),
            (
                "loss_of_consciousness",
                "Have you recently lost consciousness without explanation?",
                260,
            ),
            (
                "medical_red_flags",
                "Has a professional told you to avoid exercise pending review?",
                270,
            ),
        )
    ),
    AssessmentQuestion(
        id="sports",
        category=QuestionCategory.SPORTS,
        title="Which sports are part of your current training?",
        type=QuestionType.MULTIPLE_CHOICE,
        options=_options(
            ("football", "Football"),
            ("running", "Running"),
            ("strength_sport", "Strength sport"),
            ("other", "Other"),
        ),
        display_order=280,
        version=1,
    ),
    AssessmentQuestion(
        id="football_position",
        category=QuestionCategory.FOOTBALL,
        title="What is your primary football position?",
        type=QuestionType.SINGLE_CHOICE,
        options=_options(
            ("goalkeeper", "Goalkeeper"),
            ("defender", "Defender"),
            ("midfielder", "Midfielder"),
            ("forward", "Forward"),
        ),
        visibility_rules=(_rule("sports", "football", VisibilityOperator.CONTAINS),),
        display_order=290,
        version=1,
    ),
    AssessmentQuestion(
        id="goalkeeper_focus",
        category=QuestionCategory.GOALKEEPER,
        title="Which goalkeeper qualities are the current priority?",
        type=QuestionType.MULTIPLE_CHOICE,
        options=_options(
            ("reaction", "Reaction"),
            ("jumping", "Jumping"),
            ("distribution", "Distribution"),
            ("agility", "Agility"),
        ),
        visibility_rules=(_rule("football_position", "goalkeeper"),),
        display_order=300,
        version=1,
    ),
)


@dataclass(frozen=True)
class QuestionCatalog:
    versions: dict[int, tuple[AssessmentQuestion, ...]]

    def __post_init__(self) -> None:
        engine = AdaptiveBranchingEngine()
        if not self.versions:
            raise ValueError("At least one assessment version is required.")
        for version, questions in self.versions.items():
            if any(question.version != version for question in questions):
                raise ValueError("Question version does not match its catalogue version.")
            engine.validate_catalog(list(questions))

    @property
    def latest_version(self) -> int:
        return max(self.versions)

    def get(self, version: int) -> tuple[AssessmentQuestion, ...]:
        try:
            return self.versions[version]
        except KeyError as exc:
            raise ValueError(f"Assessment catalogue version {version} is unavailable.") from exc

    def grouped(self, version: int) -> dict[QuestionCategory, tuple[AssessmentQuestion, ...]]:
        groups: dict[QuestionCategory, list[AssessmentQuestion]] = {}
        for question in self.get(version):
            groups.setdefault(question.category, []).append(question)
        return {category: tuple(questions) for category, questions in groups.items()}


_ESSENTIAL_SETUP_IDS = {
    "age",
    "height",
    "current_weight",
    "primary_goal",
    "has_injury",
    "injury_area",
    "serious_injury",
    "experience",
    "home_training",
    "equipment_available",
    "commercial_gym_equipment",
    "pregnancy",
    "medical_red_flags",
}


def _essential_setup_question(question: AssessmentQuestion) -> AssessmentQuestion:
    """Version 2 asks only what is needed for safe, initial personalization.

    Nutrition habits, target weight, sleep/stress, gender-specific branches and
    sport specialization are deliberately collected in their respective feature
    flows instead of blocking the first experience.
    """
    description = question.description
    if question.id == "medical_red_flags":
        description = (
            "For your safety, tell us if a clinician has asked you to avoid exercise or "
            "if you have a serious health concern that needs clearance."
        )
    return question.model_copy(update={"version": 2, "description": description})


VERSION_2_QUESTIONS: tuple[AssessmentQuestion, ...] = tuple(
    _essential_setup_question(question)
    for question in VERSION_1_QUESTIONS
    if question.id in _ESSENTIAL_SETUP_IDS
)


ASSESSMENT_QUESTION_CATALOG = QuestionCatalog(
    versions={1: VERSION_1_QUESTIONS, 2: VERSION_2_QUESTIONS}
)
