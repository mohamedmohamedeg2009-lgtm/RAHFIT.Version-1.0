import { useEffect } from "react";

const APP_NAME = "RAHFIT AI";

/**
 * Sets document.title to "<pageName> — RAHFIT AI" while the component is mounted
 * and restores the plain app name on unmount.
 */
export function useDocumentTitle(pageName: string): void {
  useEffect(() => {
    document.title = `${pageName} — ${APP_NAME}`;
    return () => {
      document.title = APP_NAME;
    };
  }, [pageName]);
}
