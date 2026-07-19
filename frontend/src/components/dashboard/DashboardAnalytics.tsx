import { Card } from "../ui";
import { useLocale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";

export type WeeklyActivityPoint = {
  day: string;
  dayAr: string;
  calories: number;
  activeMinutes: number;
  workouts: number;
  healthScore: number;
};
export type DashboardSectionState = "loading" | "ready" | "empty" | "error";

export function DashboardAnalytics({
  state = "empty",
  data = [],
}: {
  state?: DashboardSectionState;
  data?: WeeklyActivityPoint[];
}) {
  const { locale } = useLocale();
  const copy = dashboardCopy[locale];
  if (state === "loading")
    return (
      <Card className="p-8 animate-pulse" aria-busy="true">
        <div className="h-48 bg-[var(--color-border)] rounded-[18px]" />
      </Card>
    );
  if (state === "error")
    return (
      <Card className="p-8 text-center">
        <h3>{copy.errorTitle}</h3>
        <p>{copy.analyticsError}</p>
      </Card>
    );
  if (!data.length)
    return (
      <Card className="p-8 text-center">
        <h3>{copy.weeklyAnalytics}</h3>
        <p>
          {locale === "ar"
            ? "لا توجد تحليلات أسبوعية مسجلة بعد."
            : "No weekly analytics records yet."}
        </p>
      </Card>
    );
  const max = Math.max(
    ...data.map((point) =>
      Math.max(point.calories, point.activeMinutes, point.workouts, point.healthScore),
    ),
    1,
  );
  return (
    <Card className="dashboard-analytics-card p-6 md:p-8 rounded-[28px]">
      <span className="dashboard-eyebrow">{copy.weeklyAnalytics}</span>
      <div className="weekly-bars-container">
        {data.map((point) => (
          <div key={point.day} className="weekly-bar-wrapper">
            <div className="weekly-bar-track">
              <div
                className="weekly-bar-fill"
                style={{ height: `${(point.activeMinutes / max) * 100}%` }}
              />
            </div>
            <span className="weekly-bar-day">{locale === "ar" ? point.dayAr : point.day}</span>
            <span className="sr-only">{`${point.activeMinutes} ${copy.activeMinUnit}, ${point.calories} ${copy.kcalUnit}, ${point.workouts} ${copy.workoutsUnit}, ${point.healthScore}/100`}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
