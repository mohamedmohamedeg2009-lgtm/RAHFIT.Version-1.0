import { useMemo } from "react";
import { Info, Brain, Dumbbell, Calendar, Moon } from "lucide-react";
import { Card } from "../ui";
import { CircularProgress } from "../ui/CircularProgress";
import { useLocale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";

export type RecoveryData = {
  score: number;
  status: "excellent" | "ready" | "moderate" | "fatigued";
  recText: string;
  recTextAr: string;
  sleepScore: number;
  workloadScore: number;
  restDays: number;
  stressLevel: "low" | "medium" | "high";
  stressLevelAr: string;
};

interface DashboardRecoveryProps {
  data?: RecoveryData;
}

const defaultRecoveryData: RecoveryData = {
  score: 75,
  status: "ready",
  recText:
    "Your recent activity suggests adequate recovery. Active readiness is normal, feel free to pursue moderate workout loads.",
  recTextAr:
    "نشاطك الأخير يشير إلى استشفاء كافٍ. الجاهزية البدنية طبيعية، ويمكنك القيام بتمارين متوسطة الشدة.",
  sleepScore: 82,
  workloadScore: 68,
  restDays: 2,
  stressLevel: "low",
  stressLevelAr: "منخفض",
};

export function DashboardRecovery({ data = defaultRecoveryData }: DashboardRecoveryProps) {
  const { locale } = useLocale();
  const copy = dashboardCopy[locale];
  const isRtl = locale === "ar";

  const recData = data || defaultRecoveryData;

  const statusLabel = useMemo(() => {
    switch (recData.status) {
      case "excellent":
        return isRtl ? "استشفاء ممتاز" : "Excellent";
      case "ready":
        return isRtl ? "مستعد ومؤهل" : "Ready";
      case "moderate":
        return isRtl ? "مستعد جزئياً" : "Moderate";
      case "fatigued":
      default:
        return isRtl ? "يتطلب راحة" : "Recovery Needed";
    }
  }, [recData.status, isRtl]);

  const progressStatus = useMemo(() => {
    if (recData.score >= 80) return "excellent";
    if (recData.score >= 60) return "good";
    if (recData.score >= 40) return "attention";
    return "critical";
  }, [recData.score]);

  return (
    <Card className="p-6 rounded-[28px] border-[1px] border-[var(--color-border)] bg-[var(--color-card)] shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card-hover)] flex flex-col gap-5 h-full relative overflow-hidden">
      <div className="flex justify-between items-center z-10">
        <div>
          <span className="dashboard-eyebrow">{copy.recovery}</span>
          <h2 className="text-lg font-extrabold text-[var(--color-text-primary)] mt-0.5">
            {isRtl ? "حالة استشفاء الجسم" : "Autonomic Recovery"}
          </h2>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-6 z-10">
        <CircularProgress
          value={recData.score}
          max={100}
          size={110}
          strokeWidth={10}
          label={copy.recovery}
          status={progressStatus}
          description={statusLabel}
        />

        <div className="flex-1 flex flex-col gap-2">
          <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed bg-[var(--color-background)] p-3 border border-[var(--color-border-subtle)] rounded-xl">
            {isRtl ? recData.recTextAr : recData.recText}
          </p>
        </div>
      </div>

      {/* Contributor parameters */}
      <div className="grid grid-cols-2 gap-2 mt-2 z-10">
        <div className="flex items-center gap-2 p-2 bg-[var(--color-background)] border border-[var(--color-border-subtle)] rounded-lg">
          <Moon size={14} className="text-indigo-500" />
          <div className="flex flex-col">
            <span className="text-[10px] text-[var(--color-text-secondary)]">
              {isRtl ? "جودة النوم" : "Sleep Score"}
            </span>
            <span className="text-xs font-bold text-[var(--color-text-primary)]">
              {recData.sleepScore}%
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 p-2 bg-[var(--color-background)] border border-[var(--color-border-subtle)] rounded-lg">
          <Dumbbell size={14} className="text-amber-500" />
          <div className="flex flex-col">
            <span className="text-[10px] text-[var(--color-text-secondary)]">
              {isRtl ? "جهد التدريب" : "Training Load"}
            </span>
            <span className="text-xs font-bold text-[var(--color-text-primary)]">
              {recData.workloadScore}%
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 p-2 bg-[var(--color-background)] border border-[var(--color-border-subtle)] rounded-lg">
          <Calendar size={14} className="text-emerald-500" />
          <div className="flex flex-col">
            <span className="text-[10px] text-[var(--color-text-secondary)]">
              {isRtl ? "أيام الراحة" : "Rest Days"}
            </span>
            <span className="text-xs font-bold text-[var(--color-text-primary)]">
              {recData.restDays} {isRtl ? "يوم" : "days"}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 p-2 bg-[var(--color-background)] border border-[var(--color-border-subtle)] rounded-lg">
          <Brain size={14} className="text-purple-500" />
          <div className="flex flex-col">
            <span className="text-[10px] text-[var(--color-text-secondary)]">
              {isRtl ? "مستوى الإجهاد" : "Stress level"}
            </span>
            <span className="text-xs font-bold text-[var(--color-text-primary)]">
              {isRtl ? recData.stressLevelAr : recData.stressLevel}
            </span>
          </div>
        </div>
      </div>

      <div className="flex gap-2 items-center text-[10px] text-[var(--color-text-muted)] border-t border-[var(--color-border-subtle)] pt-3 mt-auto z-10">
        <Info size={12} className="shrink-0" />
        <span>
          {isRtl
            ? "مؤشر عافية عام ولدعم التكيف البدني فقط."
            : "Wellness metric only. Intended for adaptive physical conditioning suggestions."}
        </span>
      </div>
    </Card>
  );
}
