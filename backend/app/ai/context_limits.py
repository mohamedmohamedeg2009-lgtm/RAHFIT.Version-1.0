from dataclasses import dataclass


@dataclass(frozen=True)
class AIContextLimits:
    """Provider-neutral character and serialized-byte limits."""

    maximum_question_characters: int = 1000
    maximum_serialized_bytes: int = 12_000
    maximum_conversation_messages: int = 8
    maximum_conversation_characters: int = 2000
    maximum_progress_records: int = 7
    maximum_workout_items: int = 8
    maximum_nutrition_items: int = 8
    maximum_preference_fields: int = 3
    maximum_safety_explanations: int = 6
    maximum_text_field_characters: int = 500


AI_CONTEXT_LIMITS = AIContextLimits()
