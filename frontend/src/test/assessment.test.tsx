import type { ReactElement } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";

import { AssessmentQuestionField } from "../components/assessment/AssessmentQuestionField";
import { SafetyStatusCard } from "../components/assessment/SafetyStatusCard";
import { AssessmentContext, type AssessmentContextValue } from "../contexts/AssessmentContext";
import { LocaleProvider } from "../contexts/LocaleContext";
import AssessmentCompletedPage from "../pages/assessment/AssessmentCompletedPage";
import AssessmentResumePage from "../pages/assessment/AssessmentResumePage";
import AssessmentReviewPage from "../pages/assessment/AssessmentReviewPage";
import AssessmentWizardPage from "../pages/assessment/AssessmentWizardPage";
import type {
  AssessmentProgress,
  AssessmentQuestion,
  AssessmentResult,
  AssessmentSession,
  SafetyEvaluation,
} from "../types/assessment";

const textQuestion: AssessmentQuestion = {
  id: "preferred_name",
  category: "personal_information",
  title: "What should we call you?",
  description: "Use the name you prefer.",
  type: "text",
  required: true,
  placeholder: "Your preferred name",
  min: null,
  max: null,
  unit: null,
  options: [],
  displayOrder: 1,
  version: 1,
};

const safeEvaluation: SafetyEvaluation = {
  status: "safe",
  riskLevel: "low",
  explanations: ["No answered safety item currently triggers a restriction."],
  triggeredRuleIds: [],
};

const progress: AssessmentProgress = {
  assessmentCompleteness: 50,
  readinessScore: 50,
  missingCategories: ["goals"],
  safety: safeEvaluation,
};

function makeSession(overrides: Partial<AssessmentSession> = {}): AssessmentSession {
  return {
    id: "session-1",
    assessmentVersion: 1,
    status: "in_progress",
    answers: [],
    revision: 0,
    startedAt: "2026-01-01T00:00:00Z",
    lastActivityAt: "2026-01-01T00:00:00Z",
    completedAt: null,
    resultId: null,
    progress,
    nextQuestion: textQuestion,
    ...overrides,
  };
}

const result: AssessmentResult = {
  id: "result-1",
  sessionId: "session-1",
  assessmentVersion: 1,
  profile: { personal_information: { preferred_name: "Mona" } },
  answeredQuestionIds: ["preferred_name"],
  completedCategories: ["personal_information"],
  completionPercentage: 100,
  assessmentCompleteness: 100,
  readinessScore: 85,
  missingCategories: [],
  safetyStatus: "caution",
  riskLevel: "medium",
  safetyExplanations: [
    "A reported injury requires conservative exercise selection and monitoring.",
  ],
  summary: {
    goals: ["Primary goal: general_fitness."],
    lifestyle: ["Reported sleep: 8 hours per night."],
    medicalConsiderations: [
      "A reported injury requires conservative exercise selection and monitoring.",
    ],
    trainingReadiness: "Ready only for conservative guidance with stated cautions.",
    equipment: ["dumbbells"],
    experience: "beginner",
  },
  generatedAt: "2026-01-01T00:00:00Z",
};

function contextValue(overrides: Partial<AssessmentContextValue> = {}): AssessmentContextValue {
  return {
    questions: [textQuestion],
    session: makeSession(),
    result: null,
    isLoading: false,
    isSaving: false,
    error: null,
    start: vi.fn(async () => makeSession()),
    resume: vi.fn(async () => makeSession()),
    loadSession: vi.fn(async () => makeSession()),
    saveAnswer: vi.fn(async () => makeSession()),
    finish: vi.fn(async () => result),
    loadLatest: vi.fn(async () => result),
    clearError: vi.fn(),
    ...overrides,
  };
}

function renderWithContext(
  element: ReactElement,
  value: AssessmentContextValue,
  initialEntry: string,
  extraRoutes?: ReactElement,
) {
  return render(
    <LocaleProvider>
      <AssessmentContext.Provider value={value}>
        <MemoryRouter initialEntries={[initialEntry]}>
          <Routes>
            {element}
            {extraRoutes}
          </Routes>
        </MemoryRouter>
      </AssessmentContext.Provider>
    </LocaleProvider>,
  );
}

beforeEach(() => {
  window.localStorage.clear();
  window.localStorage.setItem("rahfit.locale", "en");
});

describe("assessment wizard", () => {
  it("blocks navigation until required input is valid and saves before review", async () => {
    const user = userEvent.setup();
    const completedSession = makeSession({
      answers: [
        {
          questionId: textQuestion.id,
          value: "Mona",
          answeredAt: "2026-01-01T00:00:00Z",
        },
      ],
      nextQuestion: null,
      progress: { ...progress, assessmentCompleteness: 100 },
    });
    const saveAnswer = vi.fn(async () => completedSession);
    const value = contextValue({ saveAnswer });
    renderWithContext(
      <Route path="/assessment/session/:sessionId" element={<AssessmentWizardPage />} />,
      value,
      "/assessment/session/session-1",
      <Route path="/assessment/session/:sessionId/review" element={<h1>Review route</h1>} />,
    );

    const next = screen.getByRole("button", { name: /save and continue/i });
    expect(next).toBeDisabled();
    await user.type(screen.getByRole("textbox", { name: /what should we call you/i }), "Mona");
    expect(next).toBeEnabled();
    await user.click(next);

    expect(saveAnswer).toHaveBeenCalledWith("session-1", "preferred_name", "Mona");
    expect(await screen.findByRole("heading", { name: "Review route" })).toBeInTheDocument();
  });

  it("shows progress and returns to the previous answered question", async () => {
    const user = userEvent.setup();
    const secondQuestion = { ...textQuestion, id: "motivation", title: "What motivates you?" };
    const value = contextValue({
      questions: [textQuestion, secondQuestion],
      session: makeSession({
        answers: [
          {
            questionId: textQuestion.id,
            value: "Mona",
            answeredAt: "2026-01-01T00:00:00Z",
          },
        ],
        nextQuestion: secondQuestion,
      }),
    });
    renderWithContext(
      <Route path="/assessment/session/:sessionId" element={<AssessmentWizardPage />} />,
      value,
      "/assessment/session/session-1",
      <Route
        path="/assessment/session/:sessionId/question/:questionId"
        element={<h1>Previous question route</h1>}
      />,
    );

    expect(screen.getByRole("progressbar", { name: /assessment completion/i })).toHaveAttribute(
      "aria-valuenow",
      "50",
    );
    expect(screen.getByText("50", { selector: "strong" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /previous/i }));
    expect(screen.getByRole("heading", { name: "Previous question route" })).toBeInTheDocument();
  });

  it("renders boolean, checkbox, select, and slider controls", () => {
    const onChange = vi.fn();
    const choiceQuestion: AssessmentQuestion = {
      ...textQuestion,
      id: "goal",
      title: "Choose a goal",
      type: "single_choice",
      options: [
        { value: "a", label: "A" },
        { value: "b", label: "B" },
        { value: "c", label: "C" },
        { value: "d", label: "D" },
      ],
    };
    render(
      <LocaleProvider>
        <div>
          <AssessmentQuestionField
            question={{ ...textQuestion, id: "safe", title: "Are you ready?", type: "boolean" }}
            value={undefined}
            onChange={onChange}
          />
          <AssessmentQuestionField question={choiceQuestion} value="" onChange={onChange} />
          <AssessmentQuestionField
            question={{ ...choiceQuestion, id: "equipment", type: "multiple_choice" }}
            value={[]}
            onChange={onChange}
          />
          <AssessmentQuestionField
            question={{
              ...textQuestion,
              id: "stress",
              title: "Stress",
              type: "slider",
              min: 0,
              max: 10,
            }}
            value={5}
            onChange={onChange}
          />
        </div>
      </LocaleProvider>,
    );

    expect(screen.getByRole("radio", { name: "Yes" })).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: "Choose a goal" })).toBeInTheDocument();
    expect(screen.getAllByRole("checkbox")).toHaveLength(4);
    expect(screen.getByRole("slider", { name: "Stress" })).toHaveValue("5");
  });
});

describe("assessment lifecycle pages", () => {
  it("resumes a saved session and preserves progress", async () => {
    const user = userEvent.setup();
    const saved = makeSession({
      answers: [
        {
          questionId: textQuestion.id,
          value: "Mona",
          answeredAt: "2026-01-01T00:00:00Z",
        },
      ],
    });
    renderWithContext(
      <Route path="/assessment/resume/:sessionId" element={<AssessmentResumePage />} />,
      contextValue({ session: saved }),
      "/assessment/resume/session-1",
      <Route path="/assessment/session/:sessionId" element={<h1>Wizard resumed</h1>} />,
    );

    expect(screen.getByRole("progressbar", { name: "Assessment completion" })).toHaveAttribute(
      "aria-valuenow",
      "50",
    );
    await user.click(screen.getByRole("button", { name: /continue assessment/i }));
    expect(screen.getByRole("heading", { name: "Wizard resumed" })).toBeInTheDocument();
  });

  it("renders safe, caution, and stop safety states", () => {
    render(
      <LocaleProvider>
        <div>
          <SafetyStatusCard safety={safeEvaluation} />
          <SafetyStatusCard
            safety={{
              status: "caution",
              riskLevel: "medium",
              explanations: [
                "Pregnancy requires conservative guidance and appropriate professional advice.",
              ],
              triggeredRuleIds: ["pregnancy_caution"],
            }}
          />
          <SafetyStatusCard
            safety={{
              status: "stop",
              riskLevel: "critical",
              explanations: [
                "Reported chest pain requires medical clearance before personalized exercise guidance.",
              ],
              triggeredRuleIds: ["chest_pain_stop"],
            }}
          />
        </div>
      </LocaleProvider>,
    );

    expect(screen.getByText("No safety restriction detected")).toBeInTheDocument();
    expect(screen.getByText("Continue with caution")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("Safety pause required");
  });

  it("reviews answers, allows editing, and completes", async () => {
    const user = userEvent.setup();
    const finish = vi.fn(async () => result);
    const reviewed = makeSession({
      answers: [
        {
          questionId: textQuestion.id,
          value: "Mona",
          answeredAt: "2026-01-01T00:00:00Z",
        },
      ],
      nextQuestion: null,
      progress: { ...progress, assessmentCompleteness: 100, missingCategories: [] },
    });
    renderWithContext(
      <Route path="/assessment/session/:sessionId/review" element={<AssessmentReviewPage />} />,
      contextValue({ session: reviewed, finish }),
      "/assessment/session/session-1/review",
      <>
        <Route
          path="/assessment/session/:sessionId/question/:questionId"
          element={<h1>Edit route</h1>}
        />
        <Route path="/assessment/completed/:sessionId" element={<h1>Completed route</h1>} />
      </>,
    );

    expect(screen.getByText("Mona")).toBeInTheDocument();
    expect(screen.getByText("All required categories are complete.")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /^complete assessment/i }));
    expect(finish).toHaveBeenCalledWith("session-1");
    expect(await screen.findByRole("heading", { name: "Completed route" })).toBeInTheDocument();
  });

  it("celebrates completion and links to the dashboard placeholder", async () => {
    const user = userEvent.setup();
    renderWithContext(
      <Route path="/assessment/completed/:sessionId" element={<AssessmentCompletedPage />} />,
      contextValue({ result }),
      "/assessment/completed/session-1",
      <Route path="/app" element={<h1>Dashboard placeholder</h1>} />,
    );

    expect(screen.getByRole("heading", { name: "Your foundation is ready." })).toBeInTheDocument();
    expect(screen.getByText("85")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /continue to dashboard/i }));
    expect(screen.getByRole("heading", { name: "Dashboard placeholder" })).toBeInTheDocument();
  });
});
