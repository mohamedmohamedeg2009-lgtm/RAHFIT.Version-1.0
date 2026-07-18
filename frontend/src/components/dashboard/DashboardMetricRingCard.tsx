import { useMemo } from "react";
import { Info, Moon, Droplet, Flame } from "lucide-react";
import { Card } from "../ui";
import { CircularProgress } from "../ui/CircularProgress";
import { TrendIndicator } from "../ui/TrendIndicator";
import { useLocale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";

export type MetricType = "sleep" | "hydration" | "calories";

interface DashboardMetricRingCardProps {
  type: MetricType;
  current: number;
  target: number;
  previous?: number;
}

export function DashboardMetricRingCard({
  type,
  current,
  target,
  previous,
}: DashboardMetricRingCardProps) {
  const { locale } = useLocale();
  const copy = dashboardCopy[locale];
  const isRtl = locale === "ar";

  // Configuration mapper
  const config = useMemo(() => {
    switch (type) {
      case "sleep": {
        const valDiff = previous ? current - previous : 0;
        const sleepScore = Math.round((current / (target > 0 ? target : 8)) * 100);
        const statusKey = sleepScore >= 90 ? "excellent" : sleepScore >= 70 ? "good" : "attention";
        return {
          eyebrow: copy.sleepTitle,
          title: isRtl ? "ساعات النوم" : "Sleep Duration",
          unit: isRtl ? "ساعة" : "hrs",
          displayVal: `${current} / ${target}`,
          desc: `${sleepScore}% ${isRtl ? "جودة النوم" : "Sleep Score"}`,
          recText:
            sleepScore >= 80
              ? isRtl
                ? "نومك ممتاز ومستقر."
                : "Your sleep cycles are stable."
              : isRtl
                ? "تجنب التمارين المكثفة قبل النوم."
                : "Avoid intense sessions near bedtime.",
          status: statusKey as "excellent" | "good" | "attention",
          icon: <Moon size={18} className="text-indigo-500" />,
          trendVal: Math.abs(valDiff),
          trendDir:
            valDiff > 0 ? ("up" as const) : valDiff < 0 ? ("down" as const) : ("neutral" as const),
          positiveDir: "up" as const,
        };
      }
      case "hydration": {
        const remaining = Math.max(target - current, 0);
        const valDiff = previous ? current - previous : 0;
        const ratio = target > 0 ? (current / target) * 100 : 0;
        const statusKey = ratio >= 90 ? "excellent" : ratio >= 50 ? "good" : "attention";
        return {
          eyebrow: copy.hydrationTitle,
          title: isRtl ? "ترطيب الجسم" : "Hydration Intake",
          unit: "ml",
          displayVal: `${current} ${isRtl ? "مل" : "ml"}`,
          desc:
            ratio >= 100
              ? isRtl
                ? "مكتمل"
                : "Completed"
              : `${remaining}${isRtl ? " مل متبقٍ" : "ml left"}`,
          recText:
            ratio >= 60
              ? isRtl
                ? "معدل الترطيب مثالي."
                : "Hydration level is optimal."
              : isRtl
                ? "شرب الماء يزيد تدفق الدم."
                : "Log water intake to boost circulation.",
          status: statusKey as "excellent" | "good" | "attention",
          icon: <Droplet size={18} className="text-cyan-500" />,
          trendVal: Math.abs(valDiff),
          trendDir:
            valDiff > 0 ? ("up" as const) : valDiff < 0 ? ("down" as const) : ("neutral" as const),
          positiveDir: "up" as const,
        };
      }
      case "calories":
      default: {
        const remaining = Math.max(target - current, 0);
        const valDiff = previous ? current - previous : 0;
        const ratio = target > 0 ? (current / target) * 100 : 0;
        const statusKey = ratio > 100 ? "critical" : ratio >= 80 ? "good" : "neutral";
        return {
          eyebrow: copy.caloriesTitle,
          title: isRtl ? "السعرات الحرارية" : "Calories Fuel",
          unit: "kcal",
          displayVal: `${current} ${isRtl ? "سعرة" : "kcal"}`,
          desc:
            ratio > 100
              ? isRtl
                ? "تجاوزت الهدف"
                : "Over limit"
              : `${remaining}${isRtl ? " سعرة متبقية" : " kcal left"}`,
          recText:
            ratio <= 100
              ? isRtl
                ? "معدل استهلاك منضبط."
                : "Intake is within boundaries."
              : isRtl
                ? "استهلاك زائد للسعرات."
                : "Target calories exceeded daily bounds.",
          status: statusKey as "excellent" | "good" | "attention" | "critical" | "neutral",
          icon: <Flame size={18} className="text-rose-500" />,
          trendVal: Math.abs(valDiff),
          trendDir:
            valDiff > 0 ? ("up" as const) : valDiff < 0 ? ("down" as const) : ("neutral" as const),
          positiveDir: "down" as const, // Down is better for active excess calories context
        };
      }
    }
  }, [type, current, target, previous, copy, isRtl]);

  const progressColor = useMemo(() => {
    if (config.status === "excellent") return "excellent";
    if (config.status === "good") return "good";
    if (config.status === "attention" || config.status === "critical") return "attention";
    return "neutral";
  }, [config.status]);

  return (
    <Card className="p-5 rounded-[28px] border-[1px] border-[var(--color-border)] bg-[var(--color-card)] shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card-hover)] flex flex-col justify-between gap-4 h-full relative overflow-hidden">
      {/* Eyebrow & header */}
      <div className="flex justify-between items-start z-10">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-md bg-[var(--color-surface)] border border-[var(--color-border-subtle)]">
            {config.icon}
          </div>
          <div>
            <span className="text-[10px] uppercase tracking-wider text-[var(--color-text-secondary)] block">
              {config.eyebrow}
            </span>
            <h3 className="text-sm font-extrabold text-[var(--color-text-primary)] leading-tight">
              {config.title}
            </h3>
          </div>
        </div>
        {config.trendVal > 0 && (
          <TrendIndicator
            value={config.trendVal}
            direction={config.trendDir}
            label={isRtl ? "السابق" : "Prev"}
            positiveDirection={config.positiveDir}
            compact
          />
        )}
      </div>

      {/* Circle ring */}
      <div className="flex justify-center my-2 z-10">
        <CircularProgress
          value={current}
          max={target > 0 ? target : 100}
          size={100}
          strokeWidth={8}
          label={config.title}
          status={progressColor}
          displayValue={config.displayVal}
          description={config.desc}
        />
      </div>

      {/* Footer disclaimer summary */}
      <div className="border-t border-[var(--color-border-subtle)] pt-3 mt-auto flex flex-col gap-1.5 z-10">
        <p className="text-[11px] text-[var(--color-text-secondary)] leading-relaxed">
          {config.recText}
        </p>
        <span className="text-[9px] text-[var(--color-text-muted)] flex items-center gap-1">
          <Info size={10} className="shrink-0" />
          <span>{isRtl ? "مؤشر صحي وعافية عام." : "General wellness guidance score."}</span>
        </span>
      </div>
    </Card>
  );
}
