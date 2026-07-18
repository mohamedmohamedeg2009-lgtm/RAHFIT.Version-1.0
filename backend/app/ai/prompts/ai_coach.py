"""Internal instructions for a future bounded AI Coach message contract."""


def build_ai_coach_system_instructions() -> str:
    """Return the static provider instruction used by the non-public message flow."""
    return (
        "You are the RAHFIT AI Coach. Use only approved context, do not diagnose or provide "
        "medical advice, and direct urgent symptoms or injury concerns to qualified care. "
        "Keep guidance practical, conservative, and within the configured safety policy."
    )
