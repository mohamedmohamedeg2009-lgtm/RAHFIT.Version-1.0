import re
import unicodedata
from dataclasses import dataclass

from app.models.ai_classifier import (
    AICapabilityClassificationResult,
    AIClassificationReasonCode,
    AIClassifiedCapability,
    AIClassifierSpecialCapability,
    AIUnsupportedReason,
)
from app.models.ai_policy import AICapability

_SPACE_PATTERN = re.compile(r"\s+")
_ARABIC_TRANSLATION = str.maketrans(
    {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
        "ـ": "",
    }
)


class CapabilityClassificationError(Exception):
    """Raised when no meaningful current user message can be classified."""


@dataclass(frozen=True)
class _RuleMatch:
    capability: AIClassifiedCapability
    confidence: float
    matched_rules: tuple[str, ...]
    reason_code: AIClassificationReasonCode
    unsupported_reason: AIUnsupportedReason | None = None


@dataclass(frozen=True)
class _CapabilityRule:
    capability: AIClassifiedCapability
    reason_code: AIClassificationReasonCode
    exact_matches: frozenset[str]
    phrases: tuple[str, ...]
    required_keyword_groups: tuple[tuple[str, frozenset[str]], ...] = ()
    standalone_group: tuple[str, frozenset[str]] | None = None


_EXPLANATION_WORDS = frozenset(
    {
        "explain",
        "why",
        "what",
        "understand",
        "describe",
        "tell",
        "how",
        "اشرح",
        "ليه",
        "لماذا",
        "ما",
        "ماهو",
        "وضح",
        "افهم",
        "كيف",
        "كم",
    }
)
_ALTERNATIVE_WORDS = frozenset(
    {
        "alternative",
        "replace",
        "replacement",
        "substitute",
        "swap",
        "بديل",
        "بدل",
        "استبدل",
        "استبدال",
        "غير",
    }
)
_WORKOUT_WORDS = frozenset(
    {
        "workout",
        "workouts",
        "exercise",
        "exercises",
        "training",
        "movement",
        "تمرين",
        "تمارين",
        "تدريب",
        "حركه",
    }
)
_NUTRITION_WORDS = frozenset(
    {
        "nutrition",
        "meal",
        "meals",
        "food",
        "foods",
        "diet",
        "calories",
        "وجبه",
        "وجبات",
        "اكل",
        "طعام",
        "غذاء",
        "تغذيه",
        "سعرات",
    }
)

_RULES: tuple[_CapabilityRule, ...] = (
    _CapabilityRule(
        capability=AIClassifierSpecialCapability.MEDICAL_RELATED,
        reason_code=AIClassificationReasonCode.MEDICAL_INTENT_MATCHED,
        exact_matches=frozenset(
            {
                "i have chest pain",
                "اشعر بالم في الصدر",
                "عندي الم في الصدر",
                "احتاج تشخيص طبي",
            }
        ),
        phrases=(
            "chest pain",
            "heart disease",
            "medical diagnosis",
            "prescribe medication",
            "recent surgery",
            "loss of consciousness",
            "severe dizziness",
            "blood pressure",
            "الم في الصدر",
            "مرض القلب",
            "تشخيص طبي",
            "وصف دواء",
            "عمليه جراحيه",
            "فقدان الوعي",
            "دوخه شديده",
            "ضغط الدم",
        ),
        standalone_group=(
            "medical_topic",
            frozenset(
                {
                    "diagnose",
                    "diagnosis",
                    "medication",
                    "unconscious",
                    "dizzy",
                    "تشخيص",
                    "دواء",
                    "اغماء",
                    "دوخه",
                }
            ),
        ),
    ),
    _CapabilityRule(
        capability=AICapability.SUGGEST_WORKOUT_ALTERNATIVE,
        reason_code=AIClassificationReasonCode.WORKOUT_ALTERNATIVE_INTENT_MATCHED,
        exact_matches=frozenset(
            {
                "replace this exercise",
                "suggest an alternative exercise",
                "اقترح بديل للتمرين",
                "بدل هذا التمرين",
            }
        ),
        phrases=(
            "alternative exercise",
            "alternative workout",
            "replace this exercise",
            "substitute this exercise",
            "بديل للتمرين",
            "بديل لهذا التمرين",
            "استبدل التمرين",
            "غير هذا التمرين",
        ),
        required_keyword_groups=(
            ("alternative_intent", _ALTERNATIVE_WORDS),
            ("workout_topic", _WORKOUT_WORDS),
        ),
    ),
    _CapabilityRule(
        capability=AICapability.SUGGEST_NUTRITION_ALTERNATIVE,
        reason_code=AIClassificationReasonCode.NUTRITION_ALTERNATIVE_INTENT_MATCHED,
        exact_matches=frozenset(
            {
                "replace this meal",
                "suggest an alternative meal",
                "اقترح بديل للوجبه",
                "بدل هذه الوجبه",
            }
        ),
        phrases=(
            "alternative meal",
            "alternative food",
            "replace this meal",
            "substitute this food",
            "بديل للوجبه",
            "بديل لهذا الطعام",
            "استبدل الوجبه",
            "غير هذه الوجبه",
        ),
        required_keyword_groups=(
            ("alternative_intent", _ALTERNATIVE_WORDS),
            ("nutrition_topic", _NUTRITION_WORDS),
        ),
    ),
    _CapabilityRule(
        capability=AICapability.EXPLAIN_WORKOUT,
        reason_code=AIClassificationReasonCode.WORKOUT_INTENT_MATCHED,
        exact_matches=frozenset(
            {
                "explain my workout",
                "why this exercise",
                "اشرح تمريني",
                "ليه هذا التمرين",
            }
        ),
        phrases=(
            "explain my workout",
            "explain this exercise",
            "why this exercise",
            "tell me about my workout",
            "اشرح تمريني",
            "اشرح هذا التمرين",
            "ليه هذا التمرين",
            "وضح خطه التمرين",
        ),
        required_keyword_groups=(
            ("explanation_intent", _EXPLANATION_WORDS),
            ("workout_topic", _WORKOUT_WORDS),
        ),
    ),
    _CapabilityRule(
        capability=AICapability.EXPLAIN_NUTRITION,
        reason_code=AIClassificationReasonCode.NUTRITION_INTENT_MATCHED,
        exact_matches=frozenset(
            {
                "explain my nutrition plan",
                "why this meal",
                "اشرح خطه التغذيه",
                "ليه هذه الوجبه",
            }
        ),
        phrases=(
            "explain my nutrition",
            "explain this meal",
            "why this meal",
            "how many calories",
            "اشرح خطه التغذيه",
            "اشرح هذه الوجبه",
            "ليه هذه الوجبه",
            "كم سعرات",
        ),
        required_keyword_groups=(
            ("explanation_intent", _EXPLANATION_WORDS),
            ("nutrition_topic", _NUTRITION_WORDS),
        ),
    ),
    _CapabilityRule(
        capability=AICapability.EXPLAIN_PROGRESS,
        reason_code=AIClassificationReasonCode.PROGRESS_INTENT_MATCHED,
        exact_matches=frozenset(
            {
                "show my progress",
                "explain my progress",
                "explain today's readiness",
                "explain my readiness",
                "اعرض تقدمي",
                "اشرح تقدمي",
                "اشرح جاهزيتي اليوم",
                "اشرح جاهزيتي",
            }
        ),
        phrases=(
            "my progress",
            "my results",
            "explain today's readiness",
            "explain my readiness",
            "am i improving",
            "weight change",
            "تقدمي",
            "نتايجي",
            "اشرح جاهزيتي اليوم",
            "اشرح جاهزيتي",
            "هل اتحسن",
            "تغير وزني",
        ),
        standalone_group=(
            "progress_topic",
            frozenset(
                {
                    "progress",
                    "results",
                    "readiness",
                    "improving",
                    "تقدم",
                    "تقدمي",
                    "جاهزيه",
                    "جاهزيتي",
                    "نتايج",
                    "نتايجي",
                    "تحسن",
                }
            ),
        ),
    ),
    _CapabilityRule(
        capability=AICapability.EXPLAIN_ASSESSMENT,
        reason_code=AIClassificationReasonCode.ASSESSMENT_INTENT_MATCHED,
        exact_matches=frozenset(
            {
                "explain my assessment",
                "explain my readiness score",
                "اشرح تقييمي",
                "اشرح درجه الاستعداد",
            }
        ),
        phrases=(
            "my assessment",
            "readiness score",
            "assessment result",
            "fitness assessment",
            "تقييمي",
            "درجه الاستعداد",
            "نتيجه التقييم",
            "تقييم اللياقه",
        ),
        standalone_group=(
            "assessment_topic",
            frozenset(
                {
                    "assessment",
                    "readiness",
                    "evaluation",
                    "تقييم",
                    "تقييمي",
                    "استعداد",
                }
            ),
        ),
    ),
    _CapabilityRule(
        capability=AICapability.SUMMARIZE,
        reason_code=AIClassificationReasonCode.SUMMARY_INTENT_MATCHED,
        exact_matches=frozenset(
            {
                "summarize",
                "give me a summary",
                "لخص",
                "اعطني ملخص",
            }
        ),
        phrases=(
            "summarize this",
            "give me a summary",
            "quick summary",
            "لخص هذا",
            "اعطني ملخص",
            "ملخص سريع",
        ),
        standalone_group=(
            "summary_intent",
            frozenset({"summarize", "summary", "recap", "لخص", "ملخص", "اختصر"}),
        ),
    ),
    _CapabilityRule(
        capability=AICapability.MOTIVATE,
        reason_code=AIClassificationReasonCode.MOTIVATION_INTENT_MATCHED,
        exact_matches=frozenset(
            {
                "motivate me",
                "encourage me",
                "حفزني",
                "شجعني",
            }
        ),
        phrases=(
            "motivate me",
            "encourage me",
            "keep me going",
            "need motivation",
            "حفزني",
            "شجعني",
            "محتاج تحفيز",
            "خليني اكمل",
        ),
        standalone_group=(
            "motivation_intent",
            frozenset(
                {
                    "motivate",
                    "motivation",
                    "encourage",
                    "حفزني",
                    "تحفيز",
                    "شجعني",
                }
            ),
        ),
    ),
)

_UNSUPPORTED_TECHNICAL_PHRASES = (
    "write code",
    "write python",
    "hack account",
    "hack database",
    "access database",
    "reveal system prompt",
    "reveal the system prompt",
    "show system prompt",
    "reveal secrets",
    "show api key",
    "show the api key",
    "اكتب كود",
    "برمج لي",
    "اخترق حساب",
    "اخترق قاعده البيانات",
    "ادخل قاعده البيانات",
    "اظهر برومبت النظام",
    "اكشف الاسرار",
    "اظهر مفتاح api",
)
_UNSUPPORTED_TECHNICAL_WORDS = frozenset(
    {
        "programming",
        "hacking",
        "database",
        "exploit",
        "malware",
        "برمجه",
        "اختراق",
        "هاكر",
        "قاعده",
        "بيانات",
    }
)
_UNSUPPORTED_UNRELATED_PHRASES = (
    "write a poem",
    "write a story",
    "creative writing",
    "اكتب قصيده",
    "اكتب قصه",
)


class CapabilityClassifier:
    """Bilingual deterministic intent classification with no external dependencies."""

    def classify(self, current_user_message: str) -> AICapabilityClassificationResult:
        normalized = self.normalize(current_user_message)
        if not normalized:
            raise CapabilityClassificationError("current_user_message_required")
        tokens = frozenset(normalized.split())

        for rule in _RULES:
            match = self._match_rule(rule, normalized, tokens)
            if match:
                return self._result(match)

        unsupported = self._unsupported_match(normalized, tokens)
        return self._result(unsupported)

    @staticmethod
    def normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKC", value).translate(_ARABIC_TRANSLATION)
        normalized = "".join(
            character for character in normalized if unicodedata.category(character) != "Mn"
        )
        normalized = "".join(
            character if not unicodedata.category(character).startswith(("P", "S")) else " "
            for character in normalized.casefold()
        )
        return _SPACE_PATTERN.sub(" ", normalized).strip()

    def _match_rule(
        self,
        rule: _CapabilityRule,
        normalized: str,
        tokens: frozenset[str],
    ) -> _RuleMatch | None:
        if normalized in rule.exact_matches:
            return _RuleMatch(
                rule.capability,
                1.0,
                (f"{rule.capability.value}_exact",),
                rule.reason_code,
            )

        if any(self._contains_phrase(normalized, phrase) for phrase in rule.phrases):
            return _RuleMatch(
                rule.capability,
                0.95,
                (f"{rule.capability.value}_phrase",),
                rule.reason_code,
            )

        if rule.required_keyword_groups:
            matched_groups = tuple(
                group_name
                for group_name, keywords in rule.required_keyword_groups
                if tokens.intersection(keywords)
            )
            if len(matched_groups) == len(rule.required_keyword_groups):
                return _RuleMatch(
                    rule.capability,
                    0.9,
                    matched_groups,
                    rule.reason_code,
                )

        if rule.standalone_group:
            group_name, keywords = rule.standalone_group
            if tokens.intersection(keywords):
                return _RuleMatch(
                    rule.capability,
                    0.75,
                    (group_name,),
                    rule.reason_code,
                )
        return None

    def _unsupported_match(self, normalized: str, tokens: frozenset[str]) -> _RuleMatch:
        if any(
            self._contains_phrase(normalized, phrase) for phrase in _UNSUPPORTED_TECHNICAL_PHRASES
        ) or tokens.intersection(_UNSUPPORTED_TECHNICAL_WORDS):
            return _RuleMatch(
                AIClassifierSpecialCapability.UNSUPPORTED,
                0.95,
                ("unsupported_technical_request",),
                AIClassificationReasonCode.UNSUPPORTED_TECHNICAL_INTENT,
                AIUnsupportedReason.PROHIBITED_TECHNICAL_REQUEST,
            )
        if any(
            self._contains_phrase(normalized, phrase) for phrase in _UNSUPPORTED_UNRELATED_PHRASES
        ):
            return _RuleMatch(
                AIClassifierSpecialCapability.UNSUPPORTED,
                0.95,
                ("unsupported_unrelated_request",),
                AIClassificationReasonCode.UNSUPPORTED_UNRELATED_INTENT,
                AIUnsupportedReason.UNRELATED_REQUEST,
            )
        return _RuleMatch(
            AIClassifierSpecialCapability.UNSUPPORTED,
            0.75,
            ("no_supported_capability",),
            AIClassificationReasonCode.NO_SUPPORTED_INTENT,
            AIUnsupportedReason.NO_SUPPORTED_INTENT,
        )

    @staticmethod
    def _contains_phrase(normalized: str, phrase: str) -> bool:
        return f" {phrase} " in f" {normalized} "

    @staticmethod
    def _result(match: _RuleMatch) -> AICapabilityClassificationResult:
        unsupported = match.capability == AIClassifierSpecialCapability.UNSUPPORTED
        return AICapabilityClassificationResult(
            capability=match.capability,
            confidence=match.confidence,
            matched_rules=match.matched_rules,
            reason_code=match.reason_code,
            requires_safety_review=not unsupported,
            unsupported_reason=match.unsupported_reason,
        )
