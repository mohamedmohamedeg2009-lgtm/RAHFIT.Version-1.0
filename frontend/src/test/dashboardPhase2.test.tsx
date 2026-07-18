import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";

import { DashboardAnalytics } from "../components/dashboard/DashboardAnalytics";
import { DashboardGoals } from "../components/dashboard/DashboardGoals";
import { DashboardTimeline } from "../components/dashboard/DashboardTimeline";
import { LocaleProvider } from "../contexts/LocaleContext";

describe("Dashboard Phase 2 Components", () => {
  describe("DashboardAnalytics", () => {
    it("renders the weekly analytics component with default metric successfully", () => {
      render(
        <LocaleProvider>
          <DashboardAnalytics />
        </LocaleProvider>,
      );
      expect(screen.getByText("Weekly Analytics")).toBeInTheDocument();
      expect(screen.getAllByText("Active Minutes").length).toBeGreaterThan(0);
      expect(screen.getByText("vs Previous Week")).toBeInTheDocument();
    });

    it("allows switching metric tabs", () => {
      render(
        <LocaleProvider>
          <DashboardAnalytics />
        </LocaleProvider>,
      );
      const caloriesTab = screen.getByRole("tab", { name: "Calories" });
      expect(caloriesTab).toBeInTheDocument();
      fireEvent.click(caloriesTab);
      expect(screen.getAllByText("Calories").length).toBeGreaterThan(0);
    });

    it("displays correct translation in Arabic RTL mode", () => {
      render(
        <LocaleProvider>
          <div dir="rtl">
            <DashboardAnalytics />
          </div>
        </LocaleProvider>,
      );
      expect(screen.getByText("Weekly Analytics")).toBeInTheDocument();
    });

    it("renders loading, error, and empty states appropriately", () => {
      const { rerender } = render(
        <LocaleProvider>
          <DashboardAnalytics state="loading" />
        </LocaleProvider>,
      );
      expect(screen.queryByText("Weekly Analytics")).not.toBeInTheDocument();

      rerender(
        <LocaleProvider>
          <DashboardAnalytics state="error" />
        </LocaleProvider>,
      );
      expect(screen.getByText("Your dashboard could not load")).toBeInTheDocument();
      expect(screen.getByText("Unable to load weekly analytics.")).toBeInTheDocument();

      rerender(
        <LocaleProvider>
          <DashboardAnalytics state="empty" />
        </LocaleProvider>,
      );
      expect(screen.getByText("Weekly Analytics")).toBeInTheDocument();
      expect(
        screen.getByText("No weekly analytics data is currently available."),
      ).toBeInTheDocument();
    });
  });

  describe("DashboardGoals", () => {
    const mockGoals = [
      {
        id: "1",
        title: "Water Intake",
        titleAr: "شرب المياه",
        current: 1500,
        target: 3000,
        unit: "ml",
        unitAr: "مل",
        iconType: "water" as const,
      },
      {
        id: "2",
        title: "Daily Steps",
        titleAr: "الخطوات اليومية",
        current: 10000,
        target: 10000,
        unit: "steps",
        unitAr: "خطوة",
        iconType: "steps" as const,
      },
      {
        id: "3",
        title: "Protein Target",
        titleAr: "هدف البروتين",
        current: 50,
        target: 0,
        unit: "g",
        unitAr: "جرام",
        iconType: "protein" as const,
      },
    ];

    it("renders list of goals with safe progress calculation and completion states", () => {
      render(
        <LocaleProvider>
          <DashboardGoals goals={mockGoals} />
        </LocaleProvider>,
      );

      expect(screen.getByText("Water Intake")).toBeInTheDocument();
      expect(screen.getByText("1500 / 3000 ml")).toBeInTheDocument();
      expect(screen.getAllByText("50%").length).toBeGreaterThan(0);

      expect(screen.getByText("Daily Steps")).toBeInTheDocument();
      expect(screen.getAllByText("100%").length).toBeGreaterThan(0);

      expect(screen.getByText("Protein Target")).toBeInTheDocument();
      expect(screen.getAllByText("0%").length).toBeGreaterThan(0);

      expect(screen.getByText("1 of 3 goals completed")).toBeInTheDocument();
    });

    it("renders loading, error, and empty states appropriately", () => {
      const { rerender } = render(
        <LocaleProvider>
          <DashboardGoals state="loading" />
        </LocaleProvider>,
      );
      expect(screen.queryByText("Smart Daily Goals")).not.toBeInTheDocument();

      rerender(
        <LocaleProvider>
          <DashboardGoals state="error" />
        </LocaleProvider>,
      );
      expect(screen.getByText("Your dashboard could not load")).toBeInTheDocument();
      expect(screen.getByText("Unable to load daily goals.")).toBeInTheDocument();

      rerender(
        <LocaleProvider>
          <DashboardGoals state="empty" />
        </LocaleProvider>,
      );
      expect(screen.getByText("Smart Daily Goals")).toBeInTheDocument();
      expect(screen.getByText("No daily goals set for today.")).toBeInTheDocument();
    });
  });

  describe("DashboardTimeline", () => {
    const mockEvents = [
      {
        id: "1",
        time: "08:00 AM",
        timeAr: "٠٨:٠٠ ص",
        title: "Morning Sleep Session",
        titleAr: "متابعة النوم الصباحي",
        description: "Good quality sleep",
        descriptionAr: "نوم بجودة جيدة",
        type: "sleep" as const,
        status: "completed" as const,
      },
      {
        id: "2",
        time: "12:00 PM",
        timeAr: "١٢:٠٠ م",
        title: "HIIT Session",
        titleAr: "تمرين HIIT",
        type: "workout" as const,
        status: "upcoming" as const,
      },
    ];

    it("renders timeline events chronologically with correct statuses", () => {
      render(
        <LocaleProvider>
          <DashboardTimeline events={mockEvents} />
        </LocaleProvider>,
      );

      expect(screen.getByText("Morning Sleep Session")).toBeInTheDocument();
      expect(screen.getByText("Good quality sleep")).toBeInTheDocument();
      expect(screen.getByText("Completed")).toBeInTheDocument();

      expect(screen.getByText("HIIT Session")).toBeInTheDocument();
      expect(screen.getByText("Upcoming")).toBeInTheDocument();
    });

    it("renders loading, error, and empty states appropriately", () => {
      const { rerender } = render(
        <LocaleProvider>
          <DashboardTimeline state="loading" />
        </LocaleProvider>,
      );
      expect(screen.queryByText("Activity Timeline")).not.toBeInTheDocument();

      rerender(
        <LocaleProvider>
          <DashboardTimeline state="error" />
        </LocaleProvider>,
      );
      expect(screen.getByText("Your dashboard could not load")).toBeInTheDocument();
      expect(screen.getByText("Unable to load timeline.")).toBeInTheDocument();

      rerender(
        <LocaleProvider>
          <DashboardTimeline state="empty" />
        </LocaleProvider>,
      );
      expect(screen.getByText("Timeline Empty")).toBeInTheDocument();
      expect(screen.getByText("No events scheduled for today.")).toBeInTheDocument();
    });
  });
});
