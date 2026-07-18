import { useMemo } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export type TrendIndicatorProps = {
  value: number;
  direction: "up" | "down" | "neutral";
  label: string;
  positiveDirection?: "up" | "down";
  compact?: boolean;
};

export function TrendIndicator({
  value,
  direction,
  label,
  positiveDirection = "up",
  compact = false,
}: TrendIndicatorProps) {
  // Determine whether the trend is positive/constructive or negative/needs attention
  const isPositive = useMemo(() => {
    if (direction === "neutral") return true;
    return direction === positiveDirection;
  }, [direction, positiveDirection]);

  // Color mapping based on theme tokens
  const colorClass = useMemo(() => {
    if (direction === "neutral") return "text-[var(--color-text-muted)]";
    return isPositive
      ? "text-emerald-600 dark:text-emerald-400"
      : "text-rose-600 dark:text-rose-400";
  }, [direction, isPositive]);

  const bgClass = useMemo(() => {
    if (direction === "neutral") return "bg-gray-50 dark:bg-gray-900/20";
    return isPositive ? "bg-emerald-50 dark:bg-emerald-950/20" : "bg-rose-50 dark:bg-rose-950/20";
  }, [direction, isPositive]);

  const renderIcon = () => {
    switch (direction) {
      case "up":
        return <TrendingUp size={14} className={colorClass} />;
      case "down":
        return <TrendingDown size={14} className={colorClass} />;
      case "neutral":
      default:
        return <Minus size={14} className={colorClass} />;
    }
  };

  const trendText =
    direction === "neutral" ? "" : `${direction === "up" ? "+" : "-"}${Math.abs(value)}`;

  if (compact) {
    return (
      <span
        className={`inline-flex items-center gap-1 text-[11px] font-extrabold px-1.5 py-0.5 rounded-full ${bgClass} ${colorClass}`}
        aria-label={`${label}: ${trendText || "Stable"}`}
      >
        {renderIcon()}
        {trendText && <span>{trendText}</span>}
      </span>
    );
  }

  return (
    <div
      className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full border border-current/10 ${bgClass} ${colorClass}`}
      role="status"
      aria-label={`${label}: ${trendText || "Stable"}`}
    >
      {renderIcon()}
      {trendText && <span className="text-xs font-extrabold">{trendText}</span>}
      <span className="text-[10px] opacity-80 font-normal">{label}</span>
    </div>
  );
}
export default TrendIndicator;
