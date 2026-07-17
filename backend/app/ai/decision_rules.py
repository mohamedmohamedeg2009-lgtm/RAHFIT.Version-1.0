from collections.abc import Mapping, Sequence

# Central Threshold Constants
MIN_SAFE_SLEEP_HOURS = 5.0
CRITICAL_SLEEP_HOURS = 4.0
MIN_SAFE_CALORIES = 1200
MAX_STRESS_LEVEL = 10
MAX_FATIGUE_LEVEL = 10
MAX_SORENESS_LEVEL = 10
HIGH_STRESS_THRESHOLD = 7
HIGH_FATIGUE_THRESHOLD = 7
PAIN_SEVERE_THRESHOLD = 8
PAIN_MODERATE_THRESHOLD = 5


def calculate_readiness_score(
    sleep_hours: float,
    stress_level: int,
    fatigue_level: int,
    soreness_level: int,
    last_workout_adherence: float,
) -> int:
    """
    Calculates Training Readiness Score (0-100).
    Formula:
        Readiness = 100 - SleepPenalty - StressPenalty - FatiguePenalty - SorenessPenalty - AdherencePenalty
    Where:
        - SleepPenalty: if sleep < 7 hours: -10 * (7 - sleep), max -30. If sleep < 5 hours: extra -15.
        - StressPenalty: if stress_level > 4: -5 * (stress_level - 4), max -30.
        - FatiguePenalty: if fatigue_level > 3: -8 * (fatigue_level - 3), max -40.
        - SorenessPenalty: if soreness_level > 3: -6 * (soreness_level - 3), max -30.
        - AdherencePenalty: if last_workout_adherence < 50.0: -15.
    Output is clamped between 0 and 100.
    """
    penalty = 0.0

    # Sleep Penalty
    if sleep_hours < 7.0:
        penalty += min(30.0, 10.0 * (7.0 - sleep_hours))
    if sleep_hours < 5.0:
        penalty += 15.0

    # Stress Penalty
    if stress_level > 4:
        penalty += min(30.0, 5.0 * (stress_level - 4))

    # Fatigue Penalty
    if fatigue_level > 3:
        penalty += min(40.0, 8.0 * (fatigue_level - 3))

    # Soreness Penalty
    if soreness_level > 3:
        penalty += min(30.0, 6.0 * (soreness_level - 3))

    # Adherence Penalty
    if last_workout_adherence < 50.0:
        penalty += 15.0

    score = 100.0 - penalty
    return max(0, min(100, round(score)))


def calculate_recovery_score(
    sleep_hours: float,
    sleep_quality: int,  # 1 to 10
    fatigue: int,
    soreness: int,
    stress: int,
) -> int:
    """
    Calculates Recovery Score (0-100).
    Formula:
        Recovery = 80 + QualityAdjustment - FatiguePenalty - SorenessPenalty - StressPenalty
    Where:
        - QualityAdjustment: if sleep_quality >= 8: +20. If sleep_quality <= 4: -20.
        - FatiguePenalty: -5 * fatigue.
        - SorenessPenalty: -4 * soreness.
        - StressPenalty: -2 * stress.
    Output is clamped between 0 and 100.
    """
    score = 80.0

    # Sleep quality adjustment
    if sleep_quality >= 8:
        score += 20.0
    elif sleep_quality <= 4:
        score -= 20.0

    score -= 5.0 * fatigue
    score -= 4.0 * soreness
    score -= 2.0 * stress

    return max(0, min(100, round(score)))


def calculate_nutrition_adherence_score(
    target_calories: int,
    actual_calories: int,
    target_protein: float,
    actual_protein: float,
) -> int:
    """
    Calculates Nutrition Adherence Score (0-100).
    Formula:
        Score = 100 - (0.5 * CalorieDeviation% + 0.5 * ProteinDeviation%)
    Where:
        - CalorieDeviation% = abs(actual_calories - target_calories) / target_calories * 100
        - ProteinDeviation% = abs(actual_protein - target_protein) / target_protein * 100
    Output is clamped between 0 and 100.
    """
    if target_calories <= 0 or target_protein <= 0:
        return 0

    calorie_dev = abs(actual_calories - target_calories) / target_calories * 100.0
    protein_dev = abs(actual_protein - target_protein) / target_protein * 100.0

    penalty = 0.5 * calorie_dev + 0.5 * protein_dev
    score = 100.0 - penalty
    return max(0, min(100, round(score)))


def calculate_workout_adherence_score(
    recent_sessions_completion: Sequence[float],
) -> int:
    """
    Calculates Workout Adherence Score (0-100).
    Formula:
        Score = Average(completion_percentage of recent sessions)
    Defaults to 0 if no recent sessions exist.
    """
    if not recent_sessions_completion:
        return 0
    avg = sum(recent_sessions_completion) / len(recent_sessions_completion)
    return max(0, min(100, round(avg)))


def calculate_injury_risk_score(
    active_pain_areas: Mapping[str, int],  # area name -> intensity
    active_injuries: Sequence[
        Mapping[str, bool]
    ],  # list of injury flags (active, medically_cleared)
    mobility_limitations: int,  # count of limitations
) -> int:
    """
    Calculates Injury Risk Score (0-100).
    Formula:
        Risk = Sum(PainPenalties) + Sum(InjuryPenalties) + Sum(MobilityPenalties)
    Where:
        - PainPenalty: Severe pain (intensity >= 8) is +50. Moderate pain (intensity >= 5) is +20.
        - InjuryPenalty: Active, uncleared injury is +35. Active, cleared injury is +10.
        - MobilityPenalty: +10 per limitation.
    Output is clamped between 0 and 100.
    """
    risk = 0

    # Pain Penalties
    for intensity in active_pain_areas.values():
        if intensity >= PAIN_SEVERE_THRESHOLD:
            risk += 50
        elif intensity >= PAIN_MODERATE_THRESHOLD:
            risk += 20

    # Injury Penalties
    for injury in active_injuries:
        if injury.get("active", False):
            if not injury.get("medically_cleared", False):
                risk += 35
            else:
                risk += 10

    # Mobility Penalties
    risk += mobility_limitations * 10

    return max(0, min(100, risk))


def calculate_fatigue_score(
    subjective_fatigue: int,  # 1 to 10
    sleep_hours: float,
    stress_level: int,
) -> int:
    """
    Calculates Fatigue Score (0-100).
    Formula:
        Fatigue = subjective_fatigue * 10 + SleepPenalty + StressPenalty
    Where:
        - SleepPenalty: if sleep < 5h: +20. If sleep < 7h: +10.
        - StressPenalty: if stress > 7: +15.
    Output is clamped between 0 and 100.
    """
    score = subjective_fatigue * 10.0

    if sleep_hours < MIN_SAFE_SLEEP_HOURS:
        score += 20.0
    elif sleep_hours < 7.0:
        score += 10.0

    if stress_level > HIGH_STRESS_THRESHOLD:
        score += 15.0

    return max(0, min(100, round(score)))


def calculate_progress_score(
    weight_trend_pct: float,  # negative is weight loss, positive is weight gain
    primary_goal: str,
) -> int:
    """
    Calculates Progress Score (0-100).
    Formula:
        - If primary_goal is fat_loss: weight loss/stability is positive. Weight gain is penalized.
        - If primary_goal is muscle_gain: weight gain/stability is positive. Weight loss is penalized.
        - Other goals: default to 100 if change is small (<1%), otherwise penalize.
    """
    if primary_goal == "fat_loss":
        if weight_trend_pct <= 0:
            return 100
        # Penalize weight gain
        penalty = weight_trend_pct * 50.0
        return max(0, min(100, round(100 - penalty)))
    elif primary_goal == "muscle_gain":
        if weight_trend_pct >= 0:
            return 100
        # Penalize weight loss
        penalty = abs(weight_trend_pct) * 50.0
        return max(0, min(100, round(100 - penalty)))
    else:
        # Small changes are fine
        if abs(weight_trend_pct) <= 1.0:
            return 100
        penalty = (abs(weight_trend_pct) - 1.0) * 20.0
        return max(0, min(100, round(100 - penalty)))


def calculate_overall_health_score(
    readiness: int,
    recovery: int,
    nutrition_adherence: int,
    workout_adherence: int,
    injury_risk: int,
) -> int:
    """
    Calculates Overall Health/Performance Score (0-100).
    Formula:
        Overall = 0.3 * Readiness + 0.2 * Recovery + 0.2 * (100 - InjuryRisk) + 0.15 * NutritionAdherence + 0.15 * WorkoutAdherence
    """
    score = (
        0.3 * readiness
        + 0.2 * recovery
        + 0.2 * (100 - injury_risk)
        + 0.15 * nutrition_adherence
        + 0.15 * workout_adherence
    )
    return max(0, min(100, round(score)))


def calculate_data_quality_score(
    profile_complete_pct: int,
    has_workout_log: bool,
    has_nutrition_log: bool,
    subjective_recovery_present: bool,
) -> int:
    """
    Calculates Data Quality Score (0-100).
    Formula:
        DataQuality = 0.4 * ProfileCompleteness + 25 (if has_workout_log) + 25 (if has_nutrition_log) + 10 (if subjective_recovery_present)
    """
    score = 0.4 * profile_complete_pct
    if has_workout_log:
        score += 25.0
    if has_nutrition_log:
        score += 25.0
    if subjective_recovery_present:
        score += 10.0
    return max(0, min(100, round(score)))


def calculate_decision_confidence(
    data_quality: int,
    readiness_score: int,
    active_injury_present: bool,
) -> int:
    """
    Calculates Decision Confidence (0-100).
    Formula:
        Confidence = data_quality - ReadinessPenalty - InjuryPenalty
    Where:
        - ReadinessPenalty: if readiness < 50: -20.
        - InjuryPenalty: if active_injury_present: -10.
    Output is clamped between 10 and 100.
    """
    score = float(data_quality)
    if readiness_score < 50:
        score -= 20.0
    if active_injury_present:
        score -= 10.0
    return max(10, min(100, round(score)))
