import { useMemo } from "react";
import { Info, Activity, Moon, Droplet, Flame } from "lucide-react";
import { Card } from "../ui";
import { CircularProgress } from "../ui/CircularProgress";
import { TrendIndicator } from "../ui/TrendIndicator";
import { useLocale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";
import { getHealthStatus } from "./dashboardMetrics";

export type HealthScoreFactor = {
  id: string;
  label: string;
  labelAr: string;
  score: number;
  status: "excellent" | "good" | "attention" | "critical";
  iconType: "activity" | "sleep" | "hydration" | "nutrition";
};

export type HealthScoreData = {
  score: number;
  previousScore?: number;
  factors: HealthScoreFactor[];
  summary: string;
  summaryAr: string;
};

interface DashboardHealthScoreProps {
  data?: HealthScoreData;
}

const defaultHealthScoreData: HealthScoreData = {
  score: 82,
  previousScore: 78,
  summary:
    "Your overall health score is stable and improving, driven by high hydration and sleep scores.",
  summaryAr: "مؤشر الصحة العام لديك مستقر ويتحسن، بدعم من درجات الترطيب والنوم المرتفعة.",
  factors: [
    {
      id: "activity",
      label: "Activity Intensity",
      labelAr: "شدة النشاط البدني",
      score: 85,
      status: "excellent",
      iconType: "activity",
    },
    {
      id: "sleep",
      label: "Sleep Quality",
      labelAr: "جودة النوم اليومية",
      score: 80,
      status: "good",
      iconType: "sleep",
    },
    {
      id: "hydration",
      label: "Hydration Balance",
      labelAr: "توازن ترطيب الجسم",
      score: 90,
      status: "excellent",
      iconType: "hydration",
    },
    {
      id: "nutrition",
      label: "Macro Consistency",
      labelAr: "اتساق الكربوهيدرات والبروتين",
      score: 72,
      status: "good",
      iconType: "nutrition",
    },
  ],
};

export function DashboardHealthScore({ data = defaultHealthScoreData }: DashboardHealthScoreProps) {
  const { locale } = useLocale();
  const copy = dashboardCopy[locale];
  const isRtl = locale === "ar";

  const scoreData = data || defaultHealthScoreData;
  const status = getHealthStatus(scoreData.score);

  const statusLabel = useMemo(() => {
    switch (status) {
      case "excellent":
        return copy.excellent;
      case "good":
        return copy.good;
      case "attention":
        return copy.attention;
      case "critical":
      default:
        return copy.critical;
    }
  }, [status, copy]);

  const trendVal = scoreData.previousScore ? scoreData.score - scoreData.previousScore : 0;
  const trendDir = trendVal > 0 ? "up" : trendVal < 0 ? "down" : "neutral";

  const getFactorIcon = (type: HealthScoreFactor["iconType"]) => {
    switch (type) {
      case "activity":
        return <Activity size={16} className="text-amber-500" />;
      case "sleep":
        return <Moon size={16} className="text-indigo-500" />;
      case "hydration":
        return <Droplet size={16} className="text-cyan-500" />;
      case "nutrition":
      default:
        return <Flame size={16} className="text-rose-500" />;
    }
  };

  const getStatusColorClass = (itemStatus: HealthScoreFactor["status"]) => {
    switch (itemStatus) {
      case "excellent":
        return "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20 border-emerald-100 dark:border-emerald-900/30";
      case "good":
        return "text-[var(--color-primary)] bg-[var(--color-primary-light)] border-[var(--color-border-subtle)]";
      case "attention":
        return "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/20 border-amber-100 dark:border-amber-900/30";
      case "critical":
      default:
        return "text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/20 border-rose-100 dark:border-rose-900/30";
    }
  };

  return (
    <Card className="p-6 md:p-8 rounded-[28px] border-[1px] border-[var(--color-border)] bg-[var(--color-card)] shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card-hover)] flex flex-col justify-between gap-6 h-full relative overflow-hidden">
      <div className="flex justify-between items-start z-10">
        <div>
          <span className="dashboard-eyebrow">{copy.healthScore}</span>
          <h2 className="text-xl md:text-2xl font-extrabold text-[var(--color-text-primary)] mt-1">
            {isRtl ? "مؤشر صحة الجسم" : "Wellness Score Index"}
          </h2>
        </div>
        {trendVal !== 0 && (
          <TrendIndicator
            value={Math.abs(trendVal)}
            direction={trendDir}
            label={copy.previousWeek}
            positiveDirection="up"
            compact
          />
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center z-10">
        {/* Left Side: Score ring & simple details */}
        <div className="md:col-span-5 flex flex-col items-center justify-center gap-3">
          <CircularProgress
            value={scoreData.score}
            max={100}
            size={140}
            strokeWidth={12}
            label={copy.healthScore}
            status={status}
            description={statusLabel}
          />
        </div>

        {/* Right Side: Factors breakdown list */}
        <div className="md:col-span-7 flex flex-col gap-3">
          <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed italic border-l-2 border-[var(--color-primary)] pl-3 rtl:border-l-0 rtl:border-r-2 rtl:pl-0 rtl:pr-3">
            {isRtl ? scoreData.summaryAr : scoreData.summary}
          </p>

          <div className="flex flex-col gap-2 mt-2">
            {scoreData.factors.map((factor) => (
              <div
                key={factor.id}
                className="flex justify-between items-center p-2.5 bg-[var(--color-background)] border border-[var(--color-border-subtle)] rounded-xl"
              >
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border-subtle)] flex items-center justify-center">
                    {getFactorIcon(factor.iconType)}
                  </div>
                  <span className="text-xs font-bold text-[var(--color-text-primary)]">
                    {isRtl ? factor.labelAr : factor.label}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-extrabold text-[var(--color-text-primary)]">
                    {factor.score}%
                  </span>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${getStatusColorClass(factor.status)}`}
                  >
                    {factor.status === "excellent" ? copy.excellent : copy.good}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Wellness & clinical diagnostics disclaimer */}
      <div className="flex gap-2 items-start text-[10px] text-[var(--color-text-muted)] border-t border-[var(--color-border-subtle)] pt-4 mt-auto z-10">
        <Info size={14} className="shrink-0 text-[var(--color-text-secondary)]" />
        <p className="margin-0 leading-normal">
          {copy.wellnessIndicator} {copy.notMedical}
        </p>
      </div>
    </Card>
  );
}
