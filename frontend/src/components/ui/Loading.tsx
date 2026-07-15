export function Spinner({ label = "Loading" }: { label?: string }) {
  return <span className="ds-spinner" role="status" aria-label={label} />;
}
export function Skeleton({
  width = "100%",
  height = "1rem",
  className = "",
}: {
  width?: string;
  height?: string;
  className?: string;
}) {
  return (
    <span className={`ds-skeleton ${className}`} style={{ width, height }} aria-hidden="true" />
  );
}
export function FullPageLoader({ label = "Loading" }: { label?: string }) {
  return (
    <main className="ds-full-loader" aria-busy="true">
      <Spinner label={label} />
      <p>{label}…</p>
    </main>
  );
}
