from dataclasses import dataclass


@dataclass(frozen=True)
class AIConversationLimits:
    """Central, provider-independent storage and response limits."""

    default_page_size: int = 20
    maximum_page_size: int = 50
    maximum_title_length: int = 120
    maximum_message_length: int = 4000
    maximum_history_response: int = 100
    maximum_retained_messages: int = 500


AI_CONVERSATION_LIMITS = AIConversationLimits()
