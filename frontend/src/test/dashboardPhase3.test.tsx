import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";

import { CircularProgress } from "../components/ui/CircularProgress";
import { TrendIndicator } from "../components/ui/TrendIndicator";
import { DashboardHealthScore } from "../components/dashboard/DashboardHealthScore";
import { DashboardRecovery } from "../components/dashboard/DashboardRecovery";
import { DashboardMetricRingCard } from "../components/dashboard/DashboardMetricRingCard";
import { DashboardAIInsights } from "../components/dashboard/DashboardAIInsights";
import { buildDashboardInsights } from "../components/dashboard/dashboardMetrics";
import { LocaleProvider } from "../contexts/LocaleContext";
import type { DashboardData } from "../types/dashboard";

describe("CircularProgress Component", () => {
  it("renders progress percentage within bounds correctly", () => {
    render(
      <LocaleProvider>
        <CircularProgress value={75} max={100} label="Test Progress" />
      </LocaleProvider>,
    );
    const progressEl = screen.getByRole("progressbar");
    expect(progressEl).toBeInTheDocument();
    expect(progressEl).toHaveAttribute("aria-valuenow", "75");
    expect(progressEl).toHaveAttribute("aria-valuemin", "0");
    expect(progressEl).toHaveAttribute("aria-valuemax", "100");
    expect(screen.getByText("75%")).toBeInTheDocument();
  });

  it("clamps progress values to [0, max] safely", () => {
    const { rerender } = render(
      <LocaleProvider>
        <CircularProgress value={120} max={100} label="Clamped Max" />
      </LocaleProvider>,
    );
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "100");

    rerender(
      <LocaleProvider>
        <CircularProgress value={-15} max={100} label="Clamped Min" />
      </LocaleProvider>,
    );
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "0");
  });

  it("handles maximum value of zero safely", () => {
    render(
      <LocaleProvider>
        <CircularProgress value={50} max={0} label="Zero Max" />
      </LocaleProvider>,
    );
    const progressEl = screen.getByRole("progressbar");
    expect(progressEl).toHaveAttribute("aria-valuemin", "0");
    expect(progressEl).toHaveAttribute("aria-valuemax", "100");
  });
});

describe("TrendIndicator Component", () => {
  it("renders direction indicators and label text", () => {
    render(
      <LocaleProvider>
        <TrendIndicator value={12} direction="up" label="vs Last Week" />
      </LocaleProvider>,
    );
    expect(screen.getByText("+12")).toBeInTheDocument();
    expect(screen.getByText("vs Last Week")).toBeInTheDocument();
  });

  it("applies positive/negative semantic styles based on parameter flags", () => {
    render(
      <LocaleProvider>
        <TrendIndicator value={5} direction="down" label="Stress Level" positiveDirection="down" />
      </LocaleProvider>,
    );
    const indicator = screen.getByRole("status");
    expect(indicator.className).toContain("text-emerald-600");
  });
});

describe("Metric Widgets (Health Score, Recovery, and Metric Cards)", () => {
  it("renders Health Score details and contributing factors successfully", () => {
    render(
      <LocaleProvider>
        <DashboardHealthScore />
      </LocaleProvider>,
    );
    expect(screen.getByText("Wellness Score Index")).toBeInTheDocument();
    expect(screen.getByText("Activity Intensity")).toBeInTheDocument();
    expect(screen.getByText("Sleep Quality")).toBeInTheDocument();
  });

  it("renders Recovery details and recommendations safely", () => {
    render(
      <LocaleProvider>
        <DashboardRecovery />
      </LocaleProvider>,
    );
    expect(screen.getByText("Autonomic Recovery")).toBeInTheDocument();
    expect(screen.getByText("Sleep Score")).toBeInTheDocument();
  });

  it("renders Sleep, Hydration, and Calories ring cards with appropriate configuration", () => {
    render(
      <LocaleProvider>
        <DashboardMetricRingCard type="sleep" current={7.2} target={8} />
      </LocaleProvider>,
    );
    expect(screen.getByText("Sleep Duration")).toBeInTheDocument();
    expect(screen.getByText("7.2 / 8")).toBeInTheDocument();
  });
});

describe("AI Insights and Insight rules Engine", () => {
  const baseData = {
    nutrition: {
      waterConsumedMl: 1000,
      waterTargetMl: 3000,
      caloriesConsumed: 1200,
      targetCalories: 2500,
    },
    workout: { status: "completed", lastActivityAt: "2026-07-16T08:00:00Z" },
    assessment: { readinessScore: 85 },
  };

  it("generates deterministic low hydration insight rule correctly", () => {
    const insights = buildDashboardInsights(baseData as unknown as Partial<DashboardData>, "en");
    const hydrInsight = insights.find((i) => i.id === "hydration");
    expect(hydrInsight).toBeDefined();
    expect(hydrInsight?.title).toBe("Hydration Intake Check");
  });

  it("generates poor sleep / low readiness advice correctly", () => {
    const poorSleepData = {
      ...baseData,
      assessment: { readinessScore: 65 },
    };
    const insights = buildDashboardInsights(
      poorSleepData as unknown as Partial<DashboardData>,
      "en",
    );
    const sleepInsight = insights.find((i) => i.id === "sleep");
    expect(sleepInsight).toBeDefined();
    expect(sleepInsight?.title).toBe("Slight Deficit in Sleep Rest");
  });

  it("generates onboarding fallback when data is missing", () => {
    const insights = buildDashboardInsights(null, "en");
    expect(insights[0].id).toBe("onboard");
    expect(insights[0].title).toBe("Welcome to Rahafit platform");
  });

  it("renders expandable whyExplanation upon user interaction", () => {
    render(
      <LocaleProvider>
        <DashboardAIInsights dashboardData={baseData as unknown as Partial<DashboardData>} />
      </LocaleProvider>,
    );
    const whyBtn = screen.getByRole("button", { name: "Why this recommendation?" });
    expect(whyBtn).toBeInTheDocument();
    fireEvent.click(whyBtn);
    expect(screen.getByText(/Water regulates body temperature/i)).toBeInTheDocument();
  });
});
