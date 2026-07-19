"""Unit tests for AI Coach system prompt builder."""

from app.ai.prompts.ai_coach import (
    AI_COACH_PROMPT_VERSION,
    MAX_SYSTEM_INSTRUCTION_LENGTH,
    build_ai_coach_system_instructions,
)


def test_prompt_version_and_max_length() -> None:
    assert AI_COACH_PROMPT_VERSION == "rahfit-ai-coach-prompt-v1"
    instructions = build_ai_coach_system_instructions()
    assert len(instructions) <= MAX_SYSTEM_INSTRUCTION_LENGTH
    assert "Rahafit AI Coach" in instructions


def test_approved_context_and_disclaimer_rules() -> None:
    instructions = build_ai_coach_system_instructions()
    assert "Non-Medical Disclaimer" in instructions
    assert "Rahafit does NOT provide medical advice" in instructions
    assert "Approved Context Only" in instructions
    assert "Insufficient Information" in instructions
    assert "Policy Authoritativeness" in instructions


def test_forbidden_data_exclusion() -> None:
    instructions = build_ai_coach_system_instructions(custom_notes="Focus on squat form.")
    assert "mongodb://" not in instructions
    assert "SECRET" not in instructions
    assert "api_key" not in instructions
    assert "Focus on squat form." in instructions
