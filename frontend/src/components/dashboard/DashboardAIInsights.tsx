import { useState, useMemo } from "react";
import { Sparkles, ChevronDown, ChevronUp, AlertCircle } from "lucide-react";
import { Card, Badge } from "../ui";
import { useLocale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";
import { buildDashboardInsights } from "./dashboardMetrics";
import type { DashboardInsight } from "./dashboardMetrics";
import type { DashboardData } from "../../types/dashboard";

interface DashboardAIInsightsProps {
  dashboardData: Partial<DashboardData> | null;
}

export function DashboardAIInsights({ dashboardData }: DashboardAIInsightsProps) {
  const { locale } = useLocale();
  const copy = dashboardCopy[locale];
  const isRtl = locale === "ar";

  const [expandedInsightId, setExpandedInsightId] = useState<string | null>(null);

  // Generate deterministic insights based on dashboard data
  const insights = useMemo(() => {
    return buildDashboardInsights(dashboardData, locale);
  }, [dashboardData, locale]);

  // Separate highlighted top recommendation from minor insights
  const primaryInsight = useMemo(() => insights[0] || null, [insights]);
  const secondaryInsights = useMemo(() => insights.slice(1, 4), [insights]);

  const getCategoryIcon = (category: DashboardInsight["category"]) => {
    switch (category) {
      case "hydration":
        return <Sparkles size={16} className="text-cyan-500" />;
      case "sleep":
        return <Sparkles size={16} className="text-indigo-500" />;
      case "nutrition":
        return <Sparkles size={16} className="text-rose-500" />;
      case "recovery":
        return <Sparkles size={16} className="text-teal-500" />;
      case "training":
        return <Sparkles size={16} className="text-amber-500" />;
      case "general":
      default:
        return <Sparkles size={16} className="text-[var(--color-primary)]" />;
    }
  };

  const getPriorityBadge = (priority: DashboardInsight["priority"]) => {
    switch (priority) {
      case "high":
        return (
          <Badge className="bg-rose-50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 border border-rose-100 dark:border-rose-900/30 text-[10px] font-bold">
            {isRtl ? "أولوية قصوى" : "High Priority"}
          </Badge>
        );
      case "medium":
        return (
          <Badge className="bg-amber-50 dark:bg-amber-950/20 text-amber-600 dark:text-amber-400 border border-amber-100 dark:border-amber-900/30 text-[10px] font-bold">
            {isRtl ? "أولوية متوسطة" : "Medium"}
          </Badge>
        );
      case "low":
      default:
        return (
          <Badge className="bg-blue-50 dark:bg-blue-950/20 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-900/30 text-[10px] font-bold">
            {isRtl ? "نصيحة عامة" : "General Tip"}
          </Badge>
        );
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedInsightId((prev) => (prev === id ? null : id));
  };

  return (
    <Card className="p-6 md:p-8 rounded-[28px] border-[1px] border-[var(--color-border)] bg-[var(--color-card)] shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card-hover)] flex flex-col justify-between gap-6 h-full relative overflow-hidden">
      {/* Widget header */}
      <div className="flex justify-between items-center z-10">
        <div className="flex items-center gap-2">
          <Sparkles size={20} className="text-[var(--color-primary)] animate-pulse" />
          <div>
            <span className="dashboard-eyebrow">{copy.aiInsights}</span>
            <h2 className="text-xl md:text-2xl font-extrabold text-[var(--color-text-primary)] mt-1">
              {isRtl ? "استشارات الذكاء الاصطناعي" : "Rahafit AI Coach Insights"}
            </h2>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-5 z-10">
        {/* Highlighted Primary Insight */}
        {primaryInsight && (
          <div className="p-4 bg-[var(--color-background)] border border-[var(--color-border-subtle)] rounded-[20px] flex flex-col gap-3">
            <div className="flex justify-between items-start gap-4">
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border-subtle)] shrink-0">
                  {getCategoryIcon(primaryInsight.category)}
                </div>
                <h3 className="text-sm font-extrabold text-[var(--color-text-primary)]">
                  {primaryInsight.title}
                </h3>
              </div>
              {getPriorityBadge(primaryInsight.priority)}
            </div>

            <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
              {primaryInsight.description}
            </p>

            {/* Expandable Explanation Panel */}
            <div className="border-t border-[var(--color-border-subtle)] pt-3">
              <button
                onClick={() => toggleExpand(primaryInsight.id)}
                className="flex items-center gap-1.5 text-[11px] font-bold text-[var(--color-primary)] hover:opacity-80 transition-all cursor-pointer"
                aria-expanded={expandedInsightId === primaryInsight.id}
                aria-controls={`insight-explanation-${primaryInsight.id}`}
              >
                <span>{copy.whyTitle}</span>
                {expandedInsightId === primaryInsight.id ? (
                  <ChevronUp size={12} />
                ) : (
                  <ChevronDown size={12} />
                )}
              </button>

              {expandedInsightId === primaryInsight.id && (
                <div
                  id={`insight-explanation-${primaryInsight.id}`}
                  className="mt-2 text-[11px] text-[var(--color-text-secondary)] leading-relaxed bg-[var(--color-surface)] p-3 rounded-lg border border-[var(--color-border-subtle)] transition-all"
                >
                  {primaryInsight.whyExplanation}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Secondary insights list */}
        {secondaryInsights.length > 0 && (
          <div className="flex flex-col gap-2">
            <h4 className="text-xs font-extrabold text-[var(--color-text-secondary)]">
              {isRtl ? "تحليلات إضافية" : "Supporting Observations"}
            </h4>
            {secondaryInsights.map((insight) => (
              <div
                key={insight.id}
                className="flex items-center justify-between gap-4 p-3 bg-[var(--color-background)] border border-[var(--color-border-subtle)] rounded-xl"
              >
                <div className="flex items-center gap-2.5">
                  <div className="shrink-0">{getCategoryIcon(insight.category)}</div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-[var(--color-text-primary)]">
                      {insight.title}
                    </span>
                    <span className="text-[10px] text-[var(--color-text-secondary)] line-clamp-1">
                      {insight.description}
                    </span>
                  </div>
                </div>
                {getPriorityBadge(insight.priority)}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Safety medical disclaimer panel */}
      <div className="flex gap-2 items-start text-[10px] text-[var(--color-text-muted)] border-t border-[var(--color-border-subtle)] pt-4 mt-auto z-10">
        <AlertCircle size={14} className="shrink-0 text-amber-500" />
        <div className="flex flex-col">
          <span className="font-bold text-[var(--color-text-secondary)] mb-0.5">
            {copy.disclaimerTitle}
          </span>
          <p className="margin-0 leading-normal">
            {copy.wellnessIndicator} {copy.notMedical}
          </p>
        </div>
      </div>
    </Card>
  );
}
