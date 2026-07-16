import json

from app.workouts.models import WorkoutPlan


def build_workout_enhancement_instructions(plan: WorkoutPlan) -> str:
    """Build a constrained prompt; AI may explain and must echo approved IDs."""
    allowed = {
        str(day.day_number): [x.exercise_id for s in day.sections for x in s.exercises]
        for day in plan.weekly_schedule
    }
    return (
        "Echo the approved exercise IDs in exactly the supplied order and write a concise "
        "explanation. "
        "Do not add, remove, prescribe, diagnose, or change sets, reps, rest, "
        "safety notes, or days. "
        f"Return structured output for this allow-list: {json.dumps(allowed, sort_keys=True)}"
    )
