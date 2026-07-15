import type { AnswerValue, AssessmentQuestion } from "../../types/assessment";

export function initialAnswer(question: AssessmentQuestion): AnswerValue | undefined {
  if (question.type === "multiple_choice") return [];
  if (question.type === "slider") return question.min ?? 0;
  return undefined;
}

export function isAnswerReady(
  question: AssessmentQuestion,
  value: AnswerValue | undefined,
): boolean {
  if (!question.required) return true;
  if (value === undefined || value === "") return false;
  return !Array.isArray(value) || value.length > 0;
}
