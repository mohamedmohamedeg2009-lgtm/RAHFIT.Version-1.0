import { useEffect, type ReactNode } from "react";

interface OverlayProps {
  open: boolean;
  title: string;
  children: ReactNode;
  onClose: () => void;
}
export function Dialog({ open, title, children, onClose }: OverlayProps) {
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div
      className="ds-overlay"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div className="ds-dialog" role="dialog" aria-modal="true" aria-labelledby="ds-dialog-title">
        <div className="ds-overlay-header">
          <h2 id="ds-dialog-title">{title}</h2>
          <button
            type="button"
            className="ds-icon-button"
            onClick={onClose}
            aria-label="Close dialog"
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
export function Modal(props: OverlayProps) {
  return <Dialog {...props} />;
}
export function Drawer({ open, title, children, onClose }: OverlayProps) {
  return open ? (
    <div className="ds-overlay" role="presentation">
      <aside
        className="ds-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="ds-drawer-title"
      >
        <div className="ds-overlay-header">
          <h2 id="ds-drawer-title">{title}</h2>
          <button
            type="button"
            className="ds-icon-button"
            onClick={onClose}
            aria-label="Close panel"
          >
            ×
          </button>
        </div>
        {children}
      </aside>
    </div>
  ) : null;
}
