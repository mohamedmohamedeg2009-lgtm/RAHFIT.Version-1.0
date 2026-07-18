import { useMemo } from "react";
import { motion } from "framer-motion";

export type CircularProgressProps = {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  label: string;
  displayValue?: string;
  description?: string;
  trend?: {
    value: number;
    direction: "up" | "down" | "neutral";
    label: string;
  };
  status?: "excellent" | "good" | "attention" | "critical" | "neutral";
  animated?: boolean;
  className?: string;
};

export function CircularProgress({
  value,
  max = 100,
  size = 120,
  strokeWidth = 10,
  label,
  displayValue,
  description,
  status = "neutral",
  animated = true,
  className = "",
}: CircularProgressProps) {
  // Safety checks & boundaries clamping
  const safeMax = useMemo(() => (max > 0 ? max : 100), [max]);
  const boundedValue = useMemo(() => Math.min(Math.max(value, 0), safeMax), [value, safeMax]);
  const percentage = useMemo(() => (boundedValue / safeMax) * 100, [boundedValue, safeMax]);

  // SVG Geometry calculations
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = useMemo(
    () => circumference - (percentage / 100) * circumference,
    [circumference, percentage],
  );

  // Status mapping to CSS custom properties
  const statusColor = useMemo(() => {
    switch (status) {
      case "excellent":
        return "var(--color-success)";
      case "good":
        return "var(--color-primary)";
      case "attention":
        return "var(--color-warning)";
      case "critical":
        return "var(--color-danger)";
      case "neutral":
      default:
        return "var(--color-text-muted)";
    }
  }, [status]);

  const textVal = displayValue ?? `${Math.round(percentage)}%`;

  return (
    <div
      className={`circular-progress-container flex flex-col items-center justify-center text-center relative ${className}`}
      role="progressbar"
      aria-valuenow={boundedValue}
      aria-valuemin={0}
      aria-valuemax={safeMax}
      aria-label={label}
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Track circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="var(--color-border)"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="opacity-25"
        />
        {/* Indicator circle */}
        {animated ? (
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={statusColor}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.0, ease: "easeOut" }}
            strokeLinecap="round"
          />
        ) : (
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={statusColor}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
          />
        )}
      </svg>

      {/* Internal textual details */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <span
          className="font-extrabold text-[var(--color-text-primary)] leading-none"
          style={{ fontSize: size * 0.18 }}
        >
          {textVal}
        </span>
        {description && (
          <span
            className="text-[var(--color-text-secondary)] mt-1 font-semibold leading-tight px-2 text-center"
            style={{ fontSize: size * 0.08 }}
          >
            {description}
          </span>
        )}
      </div>
    </div>
  );
}
