import { useMemo } from "react";
import { motion } from "framer-motion";
import {
  Dumbbell,
  Utensils,
  Droplet,
  Footprints,
  Activity,
  Moon,
  Check,
  Calendar,
  AlertCircle,
  Info,
} from "lucide-react";
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

interface DashboardTimelineProps {
  state?: DashboardSectionState;
  events?: TimelineEvent[];
}

const defaultEvents: TimelineEvent[] = [
  {
    id: "1",
    time: "07:00 AM",
    timeAr: "٠٧:٠٠ ص",
    title: "Morning Sleep Session",
    titleAr: "متابعة النوم الصباحي",
    description: "Slept for 7.2 hours with 82% quality score.",
    descriptionAr: "نوم لمدة ٧.٢ ساعات بجودة استشفاء ٨٢٪.",
    type: "sleep",
    status: "completed",
  },
  {
    id: "2",
    time: "08:30 AM",
    timeAr: "٠٨:٣٠ ص",
    title: "Pre-Workout Hydration",
    titleAr: "الترطيب قبل التمرين",
    description: "Consumed 500ml water to meet baseline hydration.",
    descriptionAr: "شرب ٥٠٠ مل من الماء للترطيب الأساسي.",
    type: "hydration",
    status: "completed",
  },
  {
    id: "3",
    time: "10:00 AM",
    timeAr: "١٠:٠٠ ص",
    title: "HIIT Strength Training",
    titleAr: "تمرين القوة المكثف HIIT",
    description: "Completed 45 minutes target strength session.",
    descriptionAr: "إكمال ٤٥ دقيقة من تدريب القوة والتحمل.",
    type: "workout",
    status: "completed",
  },
  {
    id: "4",
    time: "01:30 PM",
    timeAr: "٠١:٣٠ م",
    title: "High-Protein Lunch Meal",
    titleAr: "وجبة غداء غنية بالبروتين",
    description: "Grilled chicken breast, quinoa salad, avocado.",
    descriptionAr: "صدر دجاج مشوي، سلطة الكينوا، أفوكادو.",
    type: "meal",
    status: "completed",
  },
  {
    id: "5",
    time: "05:00 PM",
    timeAr: "٠٥:٠٠ م",
    title: "Light Outdoor Recovery Walk",
    titleAr: "مشي خفيف للاستشفاء",
    description: "20-minute recovery stroll in the park.",
    descriptionAr: "جولة مشي خفيفة لمدة ٢٠ دقيقة للاستشفاء.",
    type: "walk",
    status: "missed",
  },
  {
    id: "6",
    time: "09:30 PM",
    timeAr: "٠٩:٣٠ م",
    title: "AI Coach Nutrition Check",
    titleAr: "مراجعة التغذية الذكية",
    description: "Evaluate protein and macro metrics.",
    descriptionAr: "تقييم نسب البروتين والمغذيات الكبرى.",
    type: "recovery",
    status: "upcoming",
  },
];

export function DashboardTimeline({
  state = "ready",
  events = defaultEvents,
}: DashboardTimelineProps) {
  const { locale } = useLocale();
  const copy = dashboardCopy[locale];
  const isRtl = locale === "ar";

  const timelineEvents = useMemo(() => events || defaultEvents, [events]);

  const getEventIcon = (type: TimelineEvent["type"]) => {
    switch (type) {
      case "sleep":
        return <Moon size={16} className="text-indigo-500" />;
      case "hydration":
        return <Droplet size={16} className="text-cyan-500" />;
      case "workout":
        return <Dumbbell size={16} className="text-amber-500" />;
      case "meal":
        return <Utensils size={16} className="text-rose-500" />;
      case "walk":
        return <Footprints size={16} className="text-emerald-500" />;
      case "recovery":
      default:
        return <Activity size={16} className="text-teal-500" />;
    }
  };

  const getStatusBadge = (status: TimelineEvent["status"]) => {
    switch (status) {
      case "completed":
        return (
          <Badge className="bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/30 flex items-center gap-1 font-bold">
            <Check size={12} />
            <span>{copy.completed}</span>
          </Badge>
        );
      case "missed":
        return (
          <Badge className="bg-rose-50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 border border-rose-100 dark:border-rose-900/30 flex items-center gap-1 font-bold">
            <AlertCircle size={12} />
            <span>{copy.missed}</span>
          </Badge>
        );
      case "upcoming":
      default:
        return (
          <Badge className="bg-blue-50 dark:bg-blue-950/20 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-900/30 flex items-center gap-1 font-bold">
            <Calendar size={12} />
            <span>{copy.upcoming}</span>
          </Badge>
        );
    }
  };

  if (state === "loading") {
    return (
      <Card className="p-8 flex flex-col gap-6 rounded-[28px] border-[1px] border-[var(--color-border)] shadow-[var(--shadow-soft)] animate-pulse">
        <div className="h-6 w-32 bg-[var(--color-border)] rounded-md" />
        <div className="flex flex-col gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-4">
              <div className="h-8 w-8 rounded-full bg-[var(--color-border)]" />
              <div className="flex-1 h-12 bg-[var(--color-border)] rounded-[14px]" />
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (state === "error") {
    return (
      <Card className="p-8 text-center rounded-[28px] border-[1px] border-red-200 dark:border-red-900 bg-red-50/50 dark:bg-red-950/20 text-[var(--color-text-primary)]">
        <div className="flex flex-col items-center gap-3">
          <Info size={40} className="text-red-500" />
          <h3 className="font-bold text-[18px]">{copy.errorTitle}</h3>
          <p className="text-sm text-[var(--color-text-secondary)]">{copy.timelineError}</p>
        </div>
      </Card>
    );
  }

  if (state === "empty" || !timelineEvents.length) {
    return (
      <Card className="p-8 text-center rounded-[28px] border-[1px] border-[var(--color-border)] shadow-[var(--shadow-soft)] text-[var(--color-text-primary)]">
        <div className="flex flex-col items-center gap-3">
          <Calendar size={40} className="text-[var(--color-text-muted)]" />
          <h3 className="font-bold text-[18px]">{copy.noTimelineTitle}</h3>
          <p className="text-sm text-[var(--color-text-secondary)]">{copy.noTimelineEvents}</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="dashboard-timeline-card p-6 md:p-8 rounded-[28px] border-[1px] border-[var(--color-border)] bg-[var(--color-card)] shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card-hover)] flex flex-col gap-6">
      <div className="flex justify-between items-center z-10">
        <div>
          <span className="dashboard-eyebrow">{copy.activityTimeline}</span>
          <h2 className="text-xl md:text-2xl font-extrabold text-[var(--color-text-primary)] mt-1">
            {locale === "ar" ? "أجندة اليوم" : "Today's Agenda"}
          </h2>
        </div>
      </div>

      <div className="relative flex flex-col gap-6 pl-4 pr-4 z-10">
        {/* Timeline line */}
        <div
          className={`absolute top-2 bottom-2 w-0.5 bg-[var(--color-border)] ${
            isRtl ? "right-9" : "left-9"
          }`}
          aria-hidden="true"
        />

        {timelineEvents.map((event, index) => {
          const title = isRtl ? event.titleAr : event.title;
          const desc = isRtl ? event.descriptionAr : event.description;
          const time = isRtl ? event.timeAr : event.time;

          const isCompleted = event.status === "completed";
          const isMissed = event.status === "missed";

          return (
            <motion.div
              key={event.id}
              className="relative flex items-start gap-4"
              initial={{ opacity: 0, x: isRtl ? 15 : -15 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.05 }}
            >
              {/* Event Time */}
              <div
                className={`text-[11px] font-extrabold text-[var(--color-text-secondary)] w-16 pt-2 shrink-0 ${
                  isRtl ? "text-left pl-2" : "text-right pr-2"
                }`}
              >
                {time}
              </div>

              {/* Event Icon Point */}
              <div
                className={`relative z-10 flex items-center justify-center w-8 h-8 rounded-full border bg-[var(--color-surface)] shadow-xs shrink-0 ${
                  isCompleted
                    ? "border-emerald-200 dark:border-emerald-900/50"
                    : isMissed
                      ? "border-rose-200 dark:border-rose-900/50"
                      : "border-[var(--color-border-subtle)]"
                }`}
                aria-hidden="true"
              >
                {getEventIcon(event.type)}
              </div>

              {/* Event Box */}
              <div className="flex-1 flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 bg-[var(--color-background)] border border-[var(--color-border-subtle)] rounded-[18px]">
                <div className="flex flex-col gap-1">
                  <span
                    className={`text-sm font-bold text-[var(--color-text-primary)] ${isCompleted ? "opacity-80" : ""}`}
                  >
                    {title}
                  </span>
                  {desc && (
                    <span className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                      {desc}
                    </span>
                  )}
                </div>
                <div className="shrink-0 self-start sm:self-center">
                  {getStatusBadge(event.status)}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </Card>
  );
}
