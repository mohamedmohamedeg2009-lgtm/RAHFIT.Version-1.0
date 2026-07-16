from typing import Any

import pytest
from pydantic import ValidationError

from app.ai.providers import OpenAICompatibleProvider
from app.api.router import router
from app.models.ai_policy import (
    AIAction,
    AICapability,
    AIForbiddenAction,
    AIPolicyDecision,
    AIPolicyReasonCode,
    AIPolicyRequest,
)
from app.services.ai_policy import AIPolicyService


@pytest.mark.parametrize(
    ("capability", "action", "decision", "reason_code"),
    (
        (
            AICapability.EXPLAIN_ASSESSMENT,
            AIAction.EXPLAIN,
            AIPolicyDecision.ALLOW,
            AIPolicyReasonCode.ASSESSMENT_EXPLANATION_ALLOWED,
        ),
        (
            AICapability.EXPLAIN_WORKOUT,
            AIAction.EXPLAIN,
            AIPolicyDecision.ALLOW,
            AIPolicyReasonCode.WORKOUT_EXPLANATION_ALLOWED,
        ),
        (
            AICapability.EXPLAIN_NUTRITION,
            AIAction.EXPLAIN,
            AIPolicyDecision.ALLOW,
            AIPolicyReasonCode.NUTRITION_EXPLANATION_ALLOWED,
        ),
        (
            AICapability.EXPLAIN_PROGRESS,
            AIAction.SUMMARIZE,
            AIPolicyDecision.ALLOW,
            AIPolicyReasonCode.PROGRESS_EXPLANATION_ALLOWED,
        ),
        (
            AICapability.MOTIVATE,
            AIAction.ENCOURAGE,
            AIPolicyDecision.ALLOW,
            AIPolicyReasonCode.MOTIVATION_ALLOWED,
        ),
        (
            AICapability.SUMMARIZE,
            AIAction.SUMMARIZE,
            AIPolicyDecision.ALLOW,
            AIPolicyReasonCode.SUMMARY_ALLOWED,
        ),
        (
            AICapability.SUGGEST_WORKOUT_ALTERNATIVE,
            AIAction.RECOMMEND,
            AIPolicyDecision.ALLOW_WITH_LIMITS,
            AIPolicyReasonCode.WORKOUT_ALTERNATIVE_APPROVED_ONLY,
        ),
        (
            AICapability.SUGGEST_NUTRITION_ALTERNATIVE,
            AIAction.RECOMMEND,
            AIPolicyDecision.ALLOW_WITH_LIMITS,
            AIPolicyReasonCode.NUTRITION_ALTERNATIVE_APPROVED_ONLY,
        ),
    ),
)
def test_every_capability_has_an_explicit_primary_policy(
    capability: AICapability,
    action: AIAction,
    decision: AIPolicyDecision,
    reason_code: AIPolicyReasonCode,
) -> None:
    result = AIPolicyService().evaluate(capability, action)

    assert result.decision == decision
    assert result.reason_code == reason_code


@pytest.mark.parametrize(
    ("action", "decision", "reason_code"),
    (
        (
            AIForbiddenAction.DIAGNOSE_MEDICAL_CONDITION,
            AIPolicyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
            AIPolicyReasonCode.MEDICAL_DIAGNOSIS_REQUIRES_PROFESSIONAL,
        ),
        (
            AIForbiddenAction.PRESCRIBE_MEDICATION,
            AIPolicyDecision.DENY,
            AIPolicyReasonCode.MEDICATION_PRESCRIPTION_FORBIDDEN,
        ),
        (
            AIForbiddenAction.OVERRIDE_WORKOUT_ENGINE,
            AIPolicyDecision.DENY,
            AIPolicyReasonCode.WORKOUT_ENGINE_OVERRIDE_FORBIDDEN,
        ),
        (
            AIForbiddenAction.OVERRIDE_NUTRITION_ENGINE,
            AIPolicyDecision.DENY,
            AIPolicyReasonCode.NUTRITION_ENGINE_OVERRIDE_FORBIDDEN,
        ),
        (
            AIForbiddenAction.IGNORE_SAFETY_RESTRICTIONS,
            AIPolicyDecision.DENY,
            AIPolicyReasonCode.SAFETY_OVERRIDE_FORBIDDEN,
        ),
        (
            AIForbiddenAction.REVEAL_SYSTEM_PROMPT,
            AIPolicyDecision.DENY,
            AIPolicyReasonCode.SYSTEM_PROMPT_DISCLOSURE_FORBIDDEN,
        ),
        (
            AIForbiddenAction.REVEAL_INTERNAL_CONTEXT,
            AIPolicyDecision.DENY,
            AIPolicyReasonCode.INTERNAL_CONTEXT_DISCLOSURE_FORBIDDEN,
        ),
        (
            AIForbiddenAction.REVEAL_SECRETS,
            AIPolicyDecision.DENY,
            AIPolicyReasonCode.SECRET_DISCLOSURE_FORBIDDEN,
        ),
        (
            AIForbiddenAction.ACCESS_DATABASE,
            AIPolicyDecision.DENY,
            AIPolicyReasonCode.DATABASE_ACCESS_FORBIDDEN,
        ),
        (
            AIForbiddenAction.EXECUTE_CODE,
            AIPolicyDecision.DENY,
            AIPolicyReasonCode.CODE_EXECUTION_FORBIDDEN,
        ),
        (
            AIForbiddenAction.INTERNET_BROWSING,
            AIPolicyDecision.DENY,
            AIPolicyReasonCode.INTERNET_BROWSING_FORBIDDEN,
        ),
    ),
)
def test_every_forbidden_action_has_an_explicit_stable_policy(
    action: AIForbiddenAction,
    decision: AIPolicyDecision,
    reason_code: AIPolicyReasonCode,
) -> None:
    result = AIPolicyService().evaluate(AICapability.EXPLAIN_WORKOUT, action)

    assert result.decision == decision
    assert result.reason_code == reason_code
    assert result.reason_code.value == str(reason_code)


@pytest.mark.parametrize("capability", tuple(AICapability))
def test_medical_diagnosis_requires_professional_guidance_for_every_capability(
    capability: AICapability,
) -> None:
    result = AIPolicyService().evaluate(
        capability,
        AIForbiddenAction.DIAGNOSE_MEDICAL_CONDITION,
    )

    assert result.decision == AIPolicyDecision.PROFESSIONAL_GUIDANCE_REQUIRED
    assert result.reason_code == AIPolicyReasonCode.MEDICAL_DIAGNOSIS_REQUIRES_PROFESSIONAL


def test_action_outside_capability_allowlist_is_denied() -> None:
    result = AIPolicyService().evaluate(
        AICapability.MOTIVATE,
        AIAction.RECOMMEND,
    )

    assert result.decision == AIPolicyDecision.DENY
    assert result.reason_code == AIPolicyReasonCode.ACTION_NOT_PERMITTED_FOR_CAPABILITY


def test_policy_request_rejects_unknown_values_and_mass_assignment() -> None:
    with pytest.raises(ValidationError):
        AIPolicyRequest.model_validate(
            {"capability": "unsupported_capability", "requested_action": "explain"}
        )
    with pytest.raises(ValidationError):
        AIPolicyRequest.model_validate(
            {"capability": "explain_workout", "requested_action": "unsupported_action"}
        )
    with pytest.raises(ValidationError):
        AIPolicyRequest.model_validate(
            {
                "capability": "explain_workout",
                "requested_action": "explain",
                "system_prompt": "client-selected-policy-override",
            }
        )


def test_decisions_and_reason_codes_are_deterministic() -> None:
    service = AIPolicyService()

    first = service.evaluate(AICapability.EXPLAIN_NUTRITION, AIAction.EXPLAIN)
    second = service.evaluate(AICapability.EXPLAIN_NUTRITION, AIAction.EXPLAIN)

    assert first == second
    assert first.model_dump(mode="json") == {
        "decision": "allow",
        "reason_code": "nutrition_explanation_allowed",
    }


def test_policy_evaluation_has_no_provider_or_prompt_behavior(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def forbidden_generate(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("Policy evaluation must never call an AI provider.")

    monkeypatch.setattr(OpenAICompatibleProvider, "generate", forbidden_generate)
    service = AIPolicyService()

    result = service.evaluate(AICapability.EXPLAIN_ASSESSMENT, AIAction.EXPLAIN)

    assert result.decision == AIPolicyDecision.ALLOW
    forbidden_methods = {
        "build_prompt",
        "generate_prompt",
        "call_provider",
        "build_context",
        "evaluate_safety",
    }
    assert forbidden_methods.isdisjoint(dir(service))


def test_policy_layer_adds_no_public_api_route() -> None:
    paths = {route.path for route in router.routes}

    assert all("policy" not in path for path in paths)


def test_policy_result_contains_only_decision_and_reason_code() -> None:
    result: dict[str, Any] = (
        AIPolicyService()
        .evaluate(
            AICapability.SUMMARIZE,
            AIAction.SUMMARIZE,
        )
        .model_dump()
    )

    assert set(result) == {"decision", "reason_code"}
