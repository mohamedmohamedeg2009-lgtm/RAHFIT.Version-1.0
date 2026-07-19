"""Unit test suite for the deterministic Daily AI Check-in readiness scoring engine."""

import pytest

from app.models.daily_check_in import (
    CheckInRecommendedAction,
    CheckInWarningCode,
    DailyCheckInInputs,
    HydrationStatus,
    ReadinessLevel,
)
from app.services.daily_check_in_engine import DailyCheckInEngine, DailyCheckInEngineError


@pytest.fixture
def engine() -> DailyCheckInEngine:
    return DailyCheckInEngine()


def test_high_readiness_produces_normal_training(engine: DailyCheckInEngine) -> None:
    inputs = DailyCheckInInputs(
        sleep_hours=8.0,
        sleep_quality=5,
        energy_level=5,
        stress_level=1,
        muscle_soreness=1,
        pain_level=0,
        hydration_status=HydrationStatus.GOOD,
        mood=5,
    )
    result = engine.calculate(inputs)

    assert result.readiness_score >= 80
    assert result.readiness_level == ReadinessLevel.HIGH
    assert result.recommended_action == CheckInRecommendedAction.NORMAL_TRAINING
    assert result.pain_flag is False
    assert len(result.warning_codes) == 0


def test_moderate_readiness_produces_reduced_intensity(engine: DailyCheckInEngine) -> None:
    inputs = DailyCheckInInputs(
        sleep_hours=6.5,
        sleep_quality=3,
        energy_level=3,
        stress_level=3,
        muscle_soreness=2,
        pain_level=0,
        hydration_status=HydrationStatus.MODERATE,
        mood=3,
    )
    result = engine.calculate(inputs)

    assert 60 <= result.readiness_score < 80
    assert result.readiness_level == ReadinessLevel.MODERATE
    assert result.recommended_action == CheckInRecommendedAction.REDUCED_INTENSITY
    assert result.pain_flag is False


def test_low_readiness_produces_recovery_session(engine: DailyCheckInEngine) -> None:
    inputs = DailyCheckInInputs(
        sleep_hours=5.5,
        sleep_quality=2,
        energy_level=2,
        stress_level=4,
        muscle_soreness=3,
        pain_level=0,
        hydration_status=HydrationStatus.LOW,
        mood=2,
    )
    result = engine.calculate(inputs)

    assert result.readiness_score < 60
    assert result.readiness_level in {ReadinessLevel.LOW, ReadinessLevel.RECOVERY_REQUIRED}
    assert result.recommended_action == CheckInRecommendedAction.RECOVERY_SESSION
    assert CheckInWarningCode.HIGH_STRESS in result.warning_codes
    assert CheckInWarningCode.DEHYDRATION in result.warning_codes


def test_high_pain_forces_rest_and_professional_guidance(engine: DailyCheckInEngine) -> None:
    # High pain (>= 7) overrides all high scores
    inputs = DailyCheckInInputs(
        sleep_hours=9.0,
        sleep_quality=5,
        energy_level=5,
        stress_level=1,
        muscle_soreness=1,
        pain_level=8,
        hydration_status=HydrationStatus.GOOD,
        mood=5,
    )
    result = engine.calculate(inputs)

    assert result.pain_flag is True
    assert CheckInWarningCode.HIGH_PAIN in result.warning_codes
    assert result.readiness_level == ReadinessLevel.RECOVERY_REQUIRED
    assert result.recommended_action == CheckInRecommendedAction.REST_AND_PROFESSIONAL_GUIDANCE
    assert result.readiness_score <= 30


def test_moderate_pain_caps_recommendation(engine: DailyCheckInEngine) -> None:
    inputs = DailyCheckInInputs(
        sleep_hours=8.0,
        sleep_quality=4,
        energy_level=4,
        stress_level=2,
        muscle_soreness=2,
        pain_level=5,
        hydration_status=HydrationStatus.GOOD,
        mood=4,
    )
    result = engine.calculate(inputs)

    assert result.pain_flag is True
    assert CheckInWarningCode.MODERATE_PAIN in result.warning_codes
    assert result.readiness_level == ReadinessLevel.LOW
    assert result.recommended_action == CheckInRecommendedAction.RECOVERY_SESSION


def test_soreness_alone_is_not_treated_as_medical_pain(engine: DailyCheckInEngine) -> None:
    # High muscle soreness (4) without pain (0)
    inputs = DailyCheckInInputs(
        sleep_hours=8.0,
        sleep_quality=4,
        energy_level=4,
        stress_level=2,
        muscle_soreness=4,
        pain_level=0,
        hydration_status=HydrationStatus.GOOD,
        mood=4,
    )
    result = engine.calculate(inputs)

    assert result.pain_flag is False
    assert CheckInWarningCode.SEVERE_SORENESS in result.warning_codes
    assert result.recommended_action == CheckInRecommendedAction.REDUCED_INTENSITY


from pydantic import ValidationError


def test_sleep_deprivation_warning(engine: DailyCheckInEngine) -> None:
    inputs = DailyCheckInInputs(
        sleep_hours=4.0,
        sleep_quality=1,
        energy_level=3,
        stress_level=2,
        muscle_soreness=2,
        pain_level=0,
        hydration_status=HydrationStatus.GOOD,
        mood=3,
    )
    result = engine.calculate(inputs)

    assert CheckInWarningCode.SLEEP_DEPRIVATION in result.warning_codes
    assert result.sleep_score <= 45


def test_multiple_fatigue_factors_warning(engine: DailyCheckInEngine) -> None:
    inputs = DailyCheckInInputs(
        sleep_hours=4.5,
        sleep_quality=2,
        energy_level=1,
        stress_level=5,
        muscle_soreness=4,
        pain_level=0,
        hydration_status=HydrationStatus.LOW,
        mood=2,
    )
    result = engine.calculate(inputs)

    assert CheckInWarningCode.MULTIPLE_FATIGUE_FACTORS in result.warning_codes
    assert result.recommended_action == CheckInRecommendedAction.RECOVERY_SESSION


def test_invalid_ranges_fail_closed(engine: DailyCheckInEngine) -> None:
    with pytest.raises(ValidationError):
        DailyCheckInInputs(
            sleep_hours=25.0,
            sleep_quality=3,
            energy_level=3,
            stress_level=3,
            muscle_soreness=3,
            pain_level=0,
            hydration_status=HydrationStatus.GOOD,
            mood=3,
        )

    with pytest.raises(ValidationError):
        DailyCheckInInputs(
            sleep_hours=8.0,
            sleep_quality=3,
            energy_level=3,
            stress_level=3,
            muscle_soreness=3,
            pain_level=11,
            hydration_status=HydrationStatus.GOOD,
            mood=3,
        )
