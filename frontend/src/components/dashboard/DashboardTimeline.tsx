import { Calendar, Dumbbell, Activity } from "lucide-react";
import { Card, Badge } from "../ui";
import { useLocale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";
import type { DashboardSectionState } from "./DashboardAnalytics";

export type TimelineEvent = {
  id: string;
  time: string;
  timeAr: string;
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  type: "workout" | "meal" | "hydration" | "walk" | "recovery" | "sleep";
  status: "completed" | "upcoming" | "missed";
};
export function DashboardTimeline({
  state = "empty",
  events = [],
}: {
  state?: DashboardSectionState;
  events?: TimelineEvent[];
}) {
  const { locale } = useLocale();
  const copy = dashboardCopy[locale];
  const rtl = locale === "ar";
  if (state === "loading")
    return (
      <Card className="p-8 animate-pulse" aria-busy="true">
        <div className="h-48 bg-[var(--color-border)]" />
      </Card>
    );
  if (state === "error")
    return (
      <Card className="p-8 text-center">
        <h3>{copy.errorTitle}</h3>
        <p>{copy.timelineError}</p>
      </Card>
    );
  if (!events.length)
    return (
      <Card className="p-8 text-center">
        <Calendar size={40} className="mx-auto" />
        <h3>{copy.noTimelineTitle}</h3>
        <p>{copy.noTimelineEvents}</p>
      </Card>
    );
  return (
    <Card className="dashboard-timeline-card p-6 md:p-8 rounded-[28px]">
      <span className="dashboard-eyebrow">{copy.activityTimeline}</span>
      <div className="flex flex-col gap-4 mt-4">
        {events.map((event) => (
          <div key={event.id} className="flex min-w-0 items-start gap-4">
            <span className="w-16 shrink-0 text-xs">{rtl ? event.timeAr : event.time}</span>
            {event.type === "workout" ? <Dumbbell size={18} className="shrink-0" /> : <Activity size={18} className="shrink-0" />}
            <div className="min-w-0 flex-1">
              <strong className="break-words">{rtl ? event.titleAr : event.title}</strong>
              {(rtl ? event.descriptionAr : event.description) && (
                <p>{rtl ? event.descriptionAr : event.description}</p>
              )}
            </div>
            <Badge className="shrink-0">
              {event.status === "completed"
                ? copy.completed
                : event.status === "missed"
                  ? copy.missed
                  : copy.upcoming}
            </Badge>
          </div>
        ))}
      </div>
    </Card>
  );
}
