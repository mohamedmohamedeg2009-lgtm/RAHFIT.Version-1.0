import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import { DashboardAnalytics } from "../components/dashboard/DashboardAnalytics";
import { DashboardTimeline } from "../components/dashboard/DashboardTimeline";
import { LocaleProvider } from "../contexts/LocaleContext";
describe("record-backed dashboard sections", () => {
  it("uses explicit empty states instead of sample analytics", () => {
    render(
      <LocaleProvider>
        <DashboardAnalytics />
      </LocaleProvider>,
    );
    expect(screen.getByText("No weekly analytics records yet.")).toBeVisible();
  });
  it("renders only supplied timeline records", () => {
    render(
      <LocaleProvider>
        <DashboardTimeline
          events={[
            {
              id: "1",
              time: "8:00 AM",
              timeAr: "٨:٠٠",
              title: "Workout recorded",
              titleAr: "تم تسجيل التمرين",
              type: "workout",
              status: "completed",
            },
          ]}
        />
      </LocaleProvider>,
    );
    expect(screen.getByText("Workout recorded")).toBeVisible();
  });
});
