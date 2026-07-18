import { useLocale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";

export type SkeletonType = "ring" | "metric" | "insight" | "card";

interface DashboardWidgetSkeletonProps {
  type?: SkeletonType;
  count?: number;
}

export function DashboardWidgetSkeleton({
  type = "card",
  count = 1,
}: DashboardWidgetSkeletonProps) {
  const { locale } = useLocale();
  const copy = dashboardCopy[locale];

  const renderSkeleton = (idx: number) => {
    switch (type) {
      case "ring":
        return (
          <div
            key={idx}
            className="flex flex-col items-center justify-center p-6 bg-[var(--color-surface)] border border-[var(--color-border-subtle)] rounded-[28px] w-full min-h-[160px] animate-pulse"
            aria-hidden="true"
          >
            {/* Circle Ring Placeholder */}
            <div className="w-20 h-20 rounded-full border-[6px] border-[var(--color-border)] opacity-40 mb-3" />
            <div className="h-4 w-16 bg-[var(--color-border)] rounded-md" />
          </div>
        );
      case "metric":
        return (
          <div
            key={idx}
            className="flex items-center gap-4 p-4 bg-[var(--color-surface)] border border-[var(--color-border-subtle)] rounded-[20px] w-full min-h-[80px] animate-pulse"
            aria-hidden="true"
          >
            <div className="w-12 h-12 rounded-full border-[4px] border-[var(--color-border)] opacity-40 shrink-0" />
            <div className="flex-1 flex flex-col gap-2">
              <div className="h-4 w-24 bg-[var(--color-border)] rounded-md" />
              <div className="h-3 w-16 bg-[var(--color-border)] rounded-md" />
            </div>
          </div>
        );
      case "insight":
        return (
          <div
            key={idx}
            className="p-6 bg-[var(--color-surface)] border border-[var(--color-border-subtle)] rounded-[28px] w-full min-h-[120px] animate-pulse flex flex-col gap-3"
            aria-hidden="true"
          >
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-md bg-[var(--color-border)] shrink-0" />
              <div className="h-4 w-32 bg-[var(--color-border)] rounded-md" />
            </div>
            <div className="h-3 w-full bg-[var(--color-border)] rounded-md" />
            <div className="h-3 w-3/4 bg-[var(--color-border)] rounded-md" />
          </div>
        );
      case "card":
      default:
        return (
          <div
            key={idx}
            className="p-6 bg-[var(--color-surface)] border border-[var(--color-border-subtle)] rounded-[28px] w-full min-h-[140px] animate-pulse flex flex-col gap-4"
            aria-hidden="true"
          >
            <div className="h-5 w-1/3 bg-[var(--color-border)] rounded-md" />
            <div className="h-12 w-full bg-[var(--color-border)] rounded-[14px]" />
          </div>
        );
    }
  };

  return (
    <div
      className="w-full flex flex-col gap-4"
      role="status"
      aria-busy="true"
      aria-label={copy.loading}
    >
      {Array.from({ length: count }).map((_, i) => renderSkeleton(i))}
    </div>
  );
}
