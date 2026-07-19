import { useMemo } from "react";
import {
  Droplet,
  Footprints,
  Flame,
  Moon,
  Dumbbell,
  CheckCircle2,
  Circle,
  Info,
} from "lucide-react";
import { Card, LinearProgress } from "../ui";
import { useLocale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";
import type { DashboardSectionState } from "./DashboardAnalytics";

export type DailyGoal = {
  id: string;
  title: string;
  titleAr: string;
  current: number;
  target: number;
  unit: string;
  unitAr: string;
  iconType: "water" | "steps" | "protein" | "sleep" | "workout";
};

interface DashboardGoalsProps {
  state?: DashboardSectionState;
  goals?: DailyGoal[];
}

const defaultGoals: DailyGoal[] = [
  {
    id: "1",
    title: "Water Intake",
    titleAr: "شرب المياه",
    current: 2000,
    target: 3000,
    unit: "ml",
    unitAr: "مل",
    iconType: "water",
  },
  {
    id: "2",
    title: "Daily Steps",
    titleAr: "الخطوات اليومية",
    current: 8400,
    target: 10000,
    unit: "steps",
    unitAr: "خطوة",
    iconType: "steps",
  },
  {
    id: "3",
    title: "Protein Target",
    titleAr: "هدف البروتين",
    current: 140,
    target: 150,
    unit: "g",
    unitAr: "جرام",
    iconType: "protein",
  },
  {
    id: "4",
    title: "Sleep Duration",
    titleAr: "ساعات النوم",
    current: 7,
    target: 8,
    unit: "hrs",
    unitAr: "ساعات",
    iconType: "sleep",
  },
  {
    id: "5",
    title: "Workout Done",
    titleAr: "إكمال التمرين",
    current: 1,
    target: 1,
    unit: "",
    unitAr: "",
    iconType: "workout",
  },
];

export function DashboardGoals({ state = "ready", goals = defaultGoals }: DashboardGoalsProps) {
  const { locale } = useLocale();
  const copy = dashboardCopy[locale];

  const currentGoals = useMemo(() => goals || defaultGoals, [goals]);

  // Compute calculated metrics
  const summary = useMemo(() => {
    if (!currentGoals.length) return { completed: 0, total: 0 };
    const completedCount = currentGoals.filter((g) => g.current >= g.target && g.target > 0).length;
    return {
      completed: completedCount,
      total: currentGoals.length,
    };
  }, [currentGoals]);

  const getGoalIcon = (type: DailyGoal["iconType"]) => {
    switch (type) {
      case "water":
        return <Droplet size={20} className="text-cyan-500" />;
      case "steps":
        return <Footprints size={20} className="text-emerald-500" />;
      case "protein":
        return <Flame size={20} className="text-rose-500" />;
      case "sleep":
        return <Moon size={20} className="text-indigo-500" />;
      case "workout":
      default:
        return <Dumbbell size={20} className="text-amber-500" />;
    }
  };

  if (state === "loading") {
    return (
      <Card className="p-8 flex flex-col gap-6 rounded-[28px] border-[1px] border-[var(--color-border)] shadow-[var(--shadow-soft)] animate-pulse">
        <div className="h-6 w-32 bg-[var(--color-border)] rounded-md" />
        <div className="grid grid-cols-1 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 w-full bg-[var(--color-border)] rounded-[18px]" />
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
          <p className="text-sm text-[var(--color-text-secondary)]">{copy.goalsError}</p>
        </div>
      </Card>
    );
  }

  if (state === "empty" || !currentGoals.length) {
    return (
      <Card className="p-8 text-center rounded-[28px] border-[1px] border-[var(--color-border)] shadow-[var(--shadow-soft)] text-[var(--color-text-primary)]">
        <div className="flex flex-col items-center gap-3">
          <CheckCircle2 size={40} className="text-[var(--color-text-muted)]" />
          <h3 className="font-bold text-[18px]">{copy.dailyGoals}</h3>
          <p className="text-sm text-[var(--color-text-secondary)]">
            {locale === "ar" ? "لا توجد أهداف يومية محددة لليوم." : "No daily goals set for today."}
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="dashboard-goals-card p-6 md:p-8 rounded-[28px] border-[1px] border-[var(--color-border)] bg-[var(--color-card)] shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card-hover)] flex flex-col gap-6 h-full justify-between">
      <div className="flex justify-between items-center z-10">
        <div>
          <span className="dashboard-eyebrow">{copy.dailyGoals}</span>
          <h2 className="text-xl md:text-2xl font-extrabold text-[var(--color-text-primary)] mt-1">
            {summary.completed} {locale === "ar" ? "من" : "of"} {summary.total}{" "}
            {copy.goalsCompleted}
          </h2>
        </div>
      </div>

      <div className="flex flex-col gap-4 z-10">
        {currentGoals.map((goal) => {
          // Safeguard division by zero and calculation clamping
          const isTargetValid = goal.target > 0;
          const rawPercentage = isTargetValid ? (goal.current / goal.target) * 100 : 0;
          const percentage = Math.min(Math.max(rawPercentage, 0), 100);
          const isCompleted = isTargetValid && goal.current >= goal.target;

          const title = locale === "ar" ? goal.titleAr : goal.title;
          const unit = locale === "ar" ? goal.unitAr : goal.unit;

          return (
            <div
              key={goal.id}
              className={`flex flex-col gap-2 p-3 rounded-[18px] transition-all border ${
                isCompleted
                  ? "bg-teal-50/20 dark:bg-teal-950/10 border-teal-100 dark:border-teal-900/30"
                  : "bg-[var(--color-background)] border-[var(--color-border-subtle)]"
              }`}
              role="listitem"
              aria-label={`${title}: ${goal.current} / ${goal.target} ${unit}, ${Math.round(percentage)}% complete`}
            >
              <div className="flex justify-between items-center gap-3">
                <div className="flex min-w-0 flex-1 items-center gap-3">
                  <div className="p-2 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border-subtle)] flex items-center justify-center shadow-xs">
                    {getGoalIcon(goal.iconType)}
                  </div>
                  <div className="min-w-0">
                    <h3
                      className={`break-words text-sm font-bold text-[var(--color-text-primary)] ${isCompleted ? "line-through opacity-70" : ""}`}
                    >
                      {title}
                    </h3>
                    <span className="text-xs text-[var(--color-text-secondary)]">
                      {goal.current} / {goal.target} {unit}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-extrabold text-[var(--color-primary)]">
                    {Math.round(percentage)}%
                  </span>
                  <div className="flex items-center justify-center" aria-hidden="true">
                    {isCompleted ? (
                      <CheckCircle2 size={18} className="text-teal-600 dark:text-teal-400" />
                    ) : (
                      <Circle size={18} className="text-[var(--color-text-muted)] opacity-60" />
                    )}
                  </div>
                </div>
              </div>

              <div className="w-full">
                <LinearProgress value={percentage} max={100} />
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
