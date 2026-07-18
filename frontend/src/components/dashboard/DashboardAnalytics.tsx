import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Flame, Clock, Trophy, Heart, TrendingUp, TrendingDown, Info } from "lucide-react";
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

interface DashboardAnalyticsProps {
  state?: DashboardSectionState;
  data?: WeeklyActivityPoint[];
}

const defaultWeeklyData: WeeklyActivityPoint[] = [
  { day: "Mon", dayAr: "ن", calories: 340, activeMinutes: 45, workouts: 1, healthScore: 78 },
  { day: "Tue", dayAr: "ث", calories: 420, activeMinutes: 50, workouts: 1, healthScore: 80 },
  { day: "Wed", dayAr: "ر", calories: 150, activeMinutes: 20, workouts: 0, healthScore: 75 },
  { day: "Thu", dayAr: "خ", calories: 510, activeMinutes: 65, workouts: 2, healthScore: 83 },
  { day: "Fri", dayAr: "ج", calories: 310, activeMinutes: 40, workouts: 1, healthScore: 81 },
  { day: "Sat", dayAr: "س", calories: 600, activeMinutes: 75, workouts: 2, healthScore: 86 },
  { day: "Sun", dayAr: "ح", calories: 200, activeMinutes: 30, workouts: 0, healthScore: 79 },
];

const prevWeekAverages = {
  calories: 320,
  activeMinutes: 42,
  workouts: 0.8,
  healthScore: 78,
};

export function DashboardAnalytics({
  state = "ready",
  data = defaultWeeklyData,
}: DashboardAnalyticsProps) {
  const { locale } = useLocale();
  const copy = dashboardCopy[locale];

  type MetricKey = "calories" | "activeMinutes" | "workouts" | "healthScore";
  const [activeMetric, setActiveMetric] = useState<MetricKey>("activeMinutes");
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const chartData = useMemo(() => data || defaultWeeklyData, [data]);

  // Compute stats for current week
  const stats = useMemo(() => {
    const total = chartData.reduce(
      (acc, item) => ({
        calories: acc.calories + item.calories,
        activeMinutes: acc.activeMinutes + item.activeMinutes,
        workouts: acc.workouts + item.workouts,
        healthScore: acc.healthScore + item.healthScore,
      }),
      { calories: 0, activeMinutes: 0, workouts: 0, healthScore: 0 },
    );

    const count = chartData.length || 1;
    const avgHealthScore = Math.round(total.healthScore / count);

    return {
      calories: {
        total: total.calories,
        average: Math.round(total.calories / count),
        prevAverage: prevWeekAverages.calories,
      },
      activeMinutes: {
        total: total.activeMinutes,
        average: Math.round(total.activeMinutes / count),
        prevAverage: prevWeekAverages.activeMinutes,
      },
      workouts: {
        total: total.workouts,
        average: Number((total.workouts / count).toFixed(1)),
        prevAverage: prevWeekAverages.workouts,
      },
      healthScore: {
        total: total.healthScore,
        average: avgHealthScore,
        prevAverage: prevWeekAverages.healthScore,
      },
    };
  }, [chartData]);

  // Retrieve current active metric summary
  const currentMetricInfo = useMemo(() => {
    const isRtl = locale === "ar";
    switch (activeMetric) {
      case "calories":
        return {
          title: copy.calories,
          value: `${stats.calories.total} ${copy.kcalUnit}`,
          averageLabel: isRtl ? "متوسط يومي" : "Daily Avg",
          averageValue: `${stats.calories.average} ${copy.kcalUnit}`,
          comparison: stats.calories.average - stats.calories.prevAverage,
          icon: <Flame size={18} className="text-rose-500" />,
          color: "#EF4444",
          gradient: ["#F87171", "#EF4444"],
          maxVal: Math.max(...chartData.map((d) => d.calories), 500),
        };
      case "workouts":
        return {
          title: copy.workouts,
          value: `${stats.workouts.total} ${copy.workoutsUnit}`,
          averageLabel: isRtl ? "متوسط يومي" : "Daily Avg",
          averageValue: `${stats.workouts.average} ${copy.workoutsUnit}`,
          comparison: stats.workouts.average - stats.workouts.prevAverage,
          icon: <Trophy size={18} className="text-amber-500" />,
          color: "#F59E0B",
          gradient: ["#FBBF24", "#F59E0B"],
          maxVal: Math.max(...chartData.map((d) => d.workouts), 3),
        };
      case "healthScore":
        return {
          title: copy.healthScore,
          value: `${stats.healthScore.average} / 100`,
          averageLabel: isRtl ? "مقارنة بالأسبوع الفائت" : "vs Last Week",
          averageValue: `${stats.healthScore.average}%`,
          comparison: stats.healthScore.average - stats.healthScore.prevAverage,
          icon: <Heart size={18} className="text-teal-500" />,
          color: "#0F766E",
          gradient: ["#14B8A6", "#0F766E"],
          maxVal: 100,
        };
      case "activeMinutes":
      default:
        return {
          title: copy.activeMinutes,
          value: `${stats.activeMinutes.total} ${copy.activeMinUnit}`,
          averageLabel: isRtl ? "متوسط يومي" : "Daily Avg",
          averageValue: `${stats.activeMinutes.average} ${copy.activeMinUnit}`,
          comparison: stats.activeMinutes.average - stats.activeMinutes.prevAverage,
          icon: <Clock size={18} className="text-cyan-500" />,
          color: "#14B8A6",
          gradient: ["#2DD4BF", "#14B8A6"],
          maxVal: Math.max(...chartData.map((d) => d.activeMinutes), 60),
        };
    }
  }, [activeMetric, stats, copy, locale, chartData]);

  if (state === "loading") {
    return (
      <Card className="p-8 flex flex-col gap-6 rounded-[28px] border-[1px] border-[var(--color-border)] shadow-[var(--shadow-soft)] animate-pulse">
        <div className="flex justify-between items-center">
          <div className="h-6 w-36 bg-[var(--color-border)] rounded-md" />
          <div className="flex gap-2">
            <div className="h-8 w-16 bg-[var(--color-border)] rounded-md" />
            <div className="h-8 w-16 bg-[var(--color-border)] rounded-md" />
          </div>
        </div>
        <div className="h-48 w-full bg-[var(--color-border)] rounded-[18px]" />
      </Card>
    );
  }

  if (state === "error") {
    return (
      <Card className="p-8 text-center rounded-[28px] border-[1px] border-red-200 dark:border-red-900 bg-red-50/50 dark:bg-red-950/20 text-[var(--color-text-primary)]">
        <div className="flex flex-col items-center gap-3">
          <Info size={40} className="text-red-500" />
          <h3 className="font-bold text-[18px]">{copy.errorTitle}</h3>
          <p className="text-sm text-[var(--color-text-secondary)]">{copy.analyticsError}</p>
        </div>
      </Card>
    );
  }

  if (state === "empty" || !chartData.length) {
    return (
      <Card className="p-8 text-center rounded-[28px] border-[1px] border-[var(--color-border)] shadow-[var(--shadow-soft)] text-[var(--color-text-primary)]">
        <div className="flex flex-col items-center gap-3">
          <Heart size={40} className="text-[var(--color-text-muted)]" />
          <h3 className="font-bold text-[18px]">{copy.weeklyAnalytics}</h3>
          <p className="text-sm text-[var(--color-text-secondary)]">
            {locale === "ar"
              ? "لا توجد تحليلات أسبوعية متاحة حالياً."
              : "No weekly analytics data is currently available."}
          </p>
        </div>
      </Card>
    );
  }

  const renderComparison = () => {
    const diff = currentMetricInfo.comparison;
    const absDiff = Math.abs(Number(diff.toFixed(1)));
    const isPositive = diff >= 0;

    if (diff === 0) return null;

    return (
      <span
        className={`flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full ${
          isPositive
            ? "bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 dark:text-emerald-400"
            : "bg-rose-50 dark:bg-rose-950/30 text-rose-600 dark:text-rose-400"
        }`}
        aria-label={`${isPositive ? "Increased" : "Decreased"} by ${absDiff} compared to previous week`}
      >
        {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
        <span>
          {isPositive ? "+" : "-"}
          {absDiff}
        </span>
        <span className="text-[10px] text-[var(--color-text-secondary)] font-normal">
          {copy.previousWeek}
        </span>
      </span>
    );
  };

  // SVG Chart sizing
  const width = 600;
  const height = 180;
  const paddingLeft = 40;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 30;

  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;
  const barCount = chartData.length;
  const itemWidth = chartWidth / barCount;
  const barWidth = Math.max(itemWidth * 0.4, 12);

  return (
    <Card className="dashboard-analytics-card p-6 md:p-8 rounded-[28px] border-[1px] border-[var(--color-border)] bg-[var(--color-card)] shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card-hover)] relative overflow-hidden flex flex-col gap-6">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 z-10">
        <div>
          <span className="dashboard-eyebrow">{copy.weeklyAnalytics}</span>
          <div className="flex items-center gap-2 mt-1">
            <h2 className="text-xl md:text-2xl font-extrabold text-[var(--color-text-primary)]">
              {currentMetricInfo.value}
            </h2>
            {renderComparison()}
          </div>
        </div>

        {/* Metric tabs */}
        <div
          className="flex bg-[var(--color-background)] p-1 rounded-xl border border-[var(--color-border)] max-w-full overflow-x-auto"
          role="tablist"
          aria-label="Weekly metrics selector"
        >
          {(
            [
              { key: "activeMinutes", icon: <Clock size={15} />, label: copy.activeMinutes },
              { key: "calories", icon: <Flame size={15} />, label: copy.calories },
              { key: "workouts", icon: <Trophy size={15} />, label: copy.workouts },
              { key: "healthScore", icon: <Heart size={15} />, label: copy.healthScore },
            ] as const
          ).map((tab) => {
            const isSelected = activeMetric === tab.key;
            return (
              <button
                key={tab.key}
                role="tab"
                aria-selected={isSelected}
                aria-label={tab.label}
                onClick={() => setActiveMetric(tab.key)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                  isSelected
                    ? "bg-[var(--color-surface)] text-[var(--color-primary)] shadow-sm"
                    : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
                }`}
              >
                {tab.icon}
                <span className="hidden md:inline">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* SVG Chart visualization */}
      <div className="relative w-full overflow-x-auto no-scrollbar" style={{ direction: "ltr" }}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          width="100%"
          height="100%"
          className="min-w-[500px]"
          aria-hidden="true"
        >
          <defs>
            <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={currentMetricInfo.gradient[0]} />
              <stop offset="100%" stopColor={currentMetricInfo.gradient[1]} />
            </linearGradient>
            <linearGradient id="glowGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={currentMetricInfo.gradient[0]} stopOpacity="0.4" />
              <stop offset="100%" stopColor={currentMetricInfo.gradient[1]} stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio, index) => {
            const y = paddingTop + chartHeight * (1 - ratio);
            const value = Math.round(ratio * currentMetricInfo.maxVal);
            return (
              <g key={index} className="opacity-40">
                <line
                  x1={paddingLeft}
                  y1={y}
                  x2={width - paddingRight}
                  y2={y}
                  stroke="var(--color-border)"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                />
                <text
                  x={paddingLeft - 8}
                  y={y + 4}
                  fill="var(--color-text-secondary)"
                  fontSize="10"
                  fontWeight="600"
                  textAnchor="end"
                >
                  {value}
                </text>
              </g>
            );
          })}

          {/* Draw bars */}
          {chartData.map((item, index) => {
            const val = item[activeMetric];
            const maxVal = currentMetricInfo.maxVal;
            const barHeight = maxVal > 0 ? (val / maxVal) * chartHeight : 0;
            const x = paddingLeft + index * itemWidth + (itemWidth - barWidth) / 2;
            const y = paddingTop + chartHeight - barHeight;

            const isHovered = hoveredIndex === index;
            const labelDay = locale === "ar" ? item.dayAr : item.day;

            return (
              <g
                key={index}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                className="cursor-pointer"
              >
                {/* Glow effect on hover */}
                {isHovered && (
                  <rect
                    x={x - 4}
                    y={y - 4}
                    width={barWidth + 8}
                    height={barHeight + 4}
                    rx="6"
                    fill="url(#glowGradient)"
                  />
                )}

                {/* Main bar */}
                <motion.rect
                  x={x}
                  y={y}
                  width={barWidth}
                  height={barHeight}
                  rx="4"
                  fill="url(#barGradient)"
                  initial={{ height: 0, y: paddingTop + chartHeight }}
                  animate={{ height: barHeight, y }}
                  transition={{ duration: 0.5, delay: index * 0.05, ease: "easeOut" }}
                />

                {/* Day Labels */}
                <text
                  x={x + barWidth / 2}
                  y={height - 8}
                  fill={isHovered ? "var(--color-primary)" : "var(--color-text-secondary)"}
                  fontSize="11"
                  fontWeight={isHovered ? "bold" : "600"}
                  textAnchor="middle"
                >
                  {labelDay}
                </text>

                {/* Tooltip value */}
                {isHovered && (
                  <g>
                    <rect
                      x={x + barWidth / 2 - 25}
                      y={y - 24}
                      width="50"
                      height="18"
                      rx="4"
                      fill="var(--color-text-primary)"
                    />
                    <text
                      x={x + barWidth / 2}
                      y={y - 12}
                      fill="var(--color-surface)"
                      fontSize="9"
                      fontWeight="bold"
                      textAnchor="middle"
                    >
                      {val}
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Screen Reader summary */}
      <span className="sr-only">
        {copy.weeklyAnalytics} data for {activeMetric}.
        {chartData
          .map((d) => ` ${locale === "ar" ? d.dayAr : d.day}: ${d[activeMetric]}`)
          .join(", ")}
      </span>

      {/* Info summary strip */}
      <div className="flex justify-between items-center text-xs text-[var(--color-text-secondary)] border-t border-[var(--color-border-subtle)] pt-4 mt-auto">
        <span className="flex items-center gap-1.5 font-semibold">
          {currentMetricInfo.icon}
          {currentMetricInfo.title}
        </span>
        <span className="font-bold text-[var(--color-text-primary)]">
          {currentMetricInfo.averageLabel}: {currentMetricInfo.averageValue}
        </span>
      </div>
    </Card>
  );
}
