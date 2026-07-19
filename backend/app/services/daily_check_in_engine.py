from app.models.daily_check_in import (
    CheckInRecommendedAction,
    CheckInWarningCode,
    DailyCheckInInputs,
    DeterministicReadinessResult,
    HydrationStatus,
    ReadinessLevel,
)


class DailyCheckInEngineError(ValueError):
    """Raised when check-in inputs fail validation or are contradictory."""


class DailyCheckInEngine:
    """Pure, deterministic readiness calculation service.

    Formula Rationale:
    1. Sub-scores (Sleep, Stress, Hydration, Recovery) are computed from 0-100 scales.
    2. Severe warnings (high pain, severe sleep deprivation, high stress, dehydration) are detected.
    3. Safety Overrides take absolute precedence over numerical averages:
       - High pain (pain_level >= 7) ALWAYS requires REST_AND_PROFESSIONAL_GUIDANCE and RECOVERY_REQUIRED.
       - Moderate pain (pain_level 4-6) caps recommendations to RECOVERY_SESSION / REDUCED_INTENSITY.
       - Muscle soreness alone is treated as fatigue (not medical pain) and caps intensity to REDUCED_INTENSITY.
       - Multiple combined fatigue factors force a RECOVERY_SESSION.
    """

    def calculate(self, inputs: DailyCheckInInputs) -> DeterministicReadinessResult:
        self._validate_inputs(inputs)

        # 1. Calculate component sub-scores (0-100)
        sleep_score = self._calc_sleep_score(inputs.sleep_hours, inputs.sleep_quality)
        stress_score = self._calc_stress_score(inputs.stress_level)
        hydration_score = self._calc_hydration_score(inputs.hydration_status)
        recovery_score = self._calc_recovery_score(
            sleep_score=sleep_score,
            energy_level=inputs.energy_level,
            muscle_soreness=inputs.muscle_soreness,
            stress_score=stress_score,
            hydration_score=hydration_score,
        )

        # 2. Base Composite Readiness Score before safety overrides
        mood_score = round((inputs.mood / 5.0) * 100)
        raw_readiness = round(
            0.50 * recovery_score
            + 0.20 * sleep_score
            + 0.15 * stress_score
            + 0.10 * hydration_score
            + 0.05 * mood_score
        )

        # 3. Detect Warning Codes
        warnings: list[CheckInWarningCode] = []
        pain_flag = False

        if inputs.pain_level >= 7:
            warnings.append(CheckInWarningCode.HIGH_PAIN)
            pain_flag = True
        elif inputs.pain_level >= 4:
            warnings.append(CheckInWarningCode.MODERATE_PAIN)
            pain_flag = True
        elif inputs.pain_level >= 1:
            pain_flag = True

        if inputs.muscle_soreness >= 4:
            warnings.append(CheckInWarningCode.SEVERE_SORENESS)

        if inputs.sleep_hours < 5.0 or inputs.sleep_quality == 1:
            warnings.append(CheckInWarningCode.SLEEP_DEPRIVATION)

        if inputs.stress_level >= 4:
            warnings.append(CheckInWarningCode.HIGH_STRESS)

        if inputs.hydration_status == HydrationStatus.LOW:
            warnings.append(CheckInWarningCode.DEHYDRATION)

        if inputs.energy_level <= 2:
            warnings.append(CheckInWarningCode.LOW_ENERGY)

        fatigue_warning_count = sum(
            1
            for w in warnings
            if w
            in {
                CheckInWarningCode.SEVERE_SORENESS,
                CheckInWarningCode.SLEEP_DEPRIVATION,
                CheckInWarningCode.HIGH_STRESS,
                CheckInWarningCode.DEHYDRATION,
                CheckInWarningCode.LOW_ENERGY,
            }
        )
        if fatigue_warning_count >= 3:
            warnings.append(CheckInWarningCode.MULTIPLE_FATIGUE_FACTORS)

        # 4. Apply Safety & Precedence Overrides
        readiness_score = raw_readiness

        if inputs.pain_level >= 7:
            readiness_score = min(readiness_score, 30)
            level = ReadinessLevel.RECOVERY_REQUIRED
            action = CheckInRecommendedAction.REST_AND_PROFESSIONAL_GUIDANCE
        elif inputs.pain_level >= 4:
            readiness_score = min(readiness_score, 50)
            level = ReadinessLevel.LOW
            action = CheckInRecommendedAction.RECOVERY_SESSION
        elif fatigue_warning_count >= 3 or inputs.sleep_hours < 4.0:
            readiness_score = min(readiness_score, 45)
            level = ReadinessLevel.LOW
            action = CheckInRecommendedAction.RECOVERY_SESSION
        elif CheckInWarningCode.SEVERE_SORENESS in warnings or inputs.energy_level == 1:
            readiness_score = min(readiness_score, 65)
            level = ReadinessLevel.MODERATE if readiness_score >= 60 else ReadinessLevel.LOW
            action = CheckInRecommendedAction.REDUCED_INTENSITY
        else:
            # Standard score-based classification
            if readiness_score >= 80 and not warnings:
                level = ReadinessLevel.HIGH
                action = CheckInRecommendedAction.NORMAL_TRAINING
            elif readiness_score >= 60:
                level = ReadinessLevel.MODERATE
                action = CheckInRecommendedAction.REDUCED_INTENSITY
            elif readiness_score >= 40:
                level = ReadinessLevel.LOW
                action = CheckInRecommendedAction.RECOVERY_SESSION
            else:
                level = ReadinessLevel.RECOVERY_REQUIRED
                action = CheckInRecommendedAction.RECOVERY_SESSION

        return DeterministicReadinessResult(
            readiness_score=max(0, min(100, readiness_score)),
            readiness_level=level,
            recovery_score=max(0, min(100, recovery_score)),
            sleep_score=max(0, min(100, sleep_score)),
            stress_score=max(0, min(100, stress_score)),
            hydration_score=max(0, min(100, hydration_score)),
            pain_flag=pain_flag,
            warning_codes=tuple(warnings),
            recommended_action=action,
        )

    @staticmethod
    def _validate_inputs(inputs: DailyCheckInInputs) -> None:
        if not (0.0 <= inputs.sleep_hours <= 24.0):
            raise DailyCheckInEngineError("sleep_hours must be between 0 and 24")
        if not (1 <= inputs.sleep_quality <= 5):
            raise DailyCheckInEngineError("sleep_quality must be between 1 and 5")
        if not (1 <= inputs.energy_level <= 5):
            raise DailyCheckInEngineError("energy_level must be between 1 and 5")
        if not (1 <= inputs.stress_level <= 5):
            raise DailyCheckInEngineError("stress_level must be between 1 and 5")
        if not (1 <= inputs.muscle_soreness <= 5):
            raise DailyCheckInEngineError("muscle_soreness must be between 1 and 5")
        if not (0 <= inputs.pain_level <= 10):
            raise DailyCheckInEngineError("pain_level must be between 0 and 10")
        if not (1 <= inputs.mood <= 5):
            raise DailyCheckInEngineError("mood must be between 1 and 5")

    @staticmethod
    def _calc_sleep_score(hours: float, quality: int) -> int:
        if 7.0 <= hours <= 9.0:
            hours_score = 100.0
        elif hours < 7.0:
            hours_score = max(0.0, (hours / 7.0) * 100.0)
        else:
            # Slightly decrease score for sleep > 9 hours
            hours_score = max(70.0, 100.0 - (hours - 9.0) * 10.0)

        quality_score = (quality / 5.0) * 100.0
        return round(0.60 * hours_score + 0.40 * quality_score)

    @staticmethod
    def _calc_stress_score(stress_level: int) -> int:
        # Inverted: 1 = 100%, 5 = 20%
        mapping = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20}
        return mapping.get(stress_level, 50)

    @staticmethod
    def _calc_hydration_score(status: HydrationStatus) -> int:
        mapping = {HydrationStatus.GOOD: 100, HydrationStatus.MODERATE: 70, HydrationStatus.LOW: 30}
        return mapping.get(status, 50)

    @staticmethod
    def _calc_recovery_score(
        *,
        sleep_score: int,
        energy_level: int,
        muscle_soreness: int,
        stress_score: int,
        hydration_score: int,
    ) -> int:
        energy_score = (energy_level / 5.0) * 100.0
        soreness_mapping = {1: 100, 2: 85, 3: 65, 4: 40, 5: 20}
        soreness_score = soreness_mapping.get(muscle_soreness, 50)

        return round(
            0.35 * sleep_score
            + 0.25 * energy_score
            + 0.20 * soreness_score
            + 0.10 * stress_score
            + 0.10 * hydration_score
        )
