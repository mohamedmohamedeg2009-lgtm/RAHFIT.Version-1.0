interface ProgressProps {
  value: number;
  max?: number;
  label?: string;
}
export function LinearProgress({ value, max = 100, label }: ProgressProps) {
  const bounded = Math.min(Math.max(value, 0), max);
  return (
    <div className="ds-progress-wrap">
      {label ? (
        <div className="ds-progress-label">
          <span>{label}</span>
          <span>{Math.round((bounded / max) * 100)}%</span>
        </div>
      ) : null}
      <div className="ds-progress-frame">
        <progress
          className="ds-progress"
          value={bounded}
          max={max}
          aria-valuenow={bounded}
          aria-valuemin={0}
          aria-valuemax={max}
          aria-label={label ?? "Progress"}
        >
          {Math.round((bounded / max) * 100)}%
        </progress>
      </div>
    </div>
  );
}
export function CircularProgress({ value, max = 100, label }: ProgressProps) {
  const bounded = Math.min(Math.max(value, 0), max);
  const percent = Math.round((bounded / max) * 100);
  return (
    <div
      className="ds-circular-progress"
      role="progressbar"
      aria-valuenow={bounded}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-label={label ?? "Progress"}
      style={{ "--progress": `${percent}%` } as React.CSSProperties}
    >
      <strong>{percent}%</strong>
    </div>
  );
}
export function StepProgress({
  current,
  total,
  label,
}: {
  current: number;
  total: number;
  label?: string;
}) {
  return (
    <div className="ds-steps" aria-label={label ?? `Step ${current} of ${total}`}>
      <span className="ds-step-summary">
        Step {current} of {total}
      </span>
      <div className="ds-step-track">
        {Array.from({ length: total }, (_, index) => (
          <span key={index} className={index < current ? "is-complete" : ""} aria-hidden="true" />
        ))}
      </div>
    </div>
  );
}
