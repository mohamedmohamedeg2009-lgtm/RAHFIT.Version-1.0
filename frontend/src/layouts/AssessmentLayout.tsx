import { Link, Outlet } from "react-router-dom";

import { Button } from "../components/ui";
import { useLocale } from "../contexts/LocaleContext";
import { useAuth } from "../hooks/useAuth";
import { assessmentCopy } from "../i18n/assessment";
import { useTheme } from "../theme";

export function AssessmentLayout() {
  const { locale, toggleLocale } = useLocale();
  const { theme, toggleTheme } = useTheme();
  const { logout } = useAuth();
  const copy = assessmentCopy[locale];

  return (
    <div className="assessment-shell">
      <header className="assessment-topbar">
        <Link
          className="assessment-brand"
          to="/assessment"
          aria-label={`${copy.brand} ${copy.assessment}`}
        >
          <span className="assessment-brand-mark" aria-hidden="true">
            R
          </span>
          <span>
            <strong>{copy.brand}</strong>
            <small>{copy.assessment}</small>
          </span>
        </Link>
        <nav className="assessment-actions" aria-label="Assessment controls">
          <Button variant="ghost" size="sm" type="button" onClick={toggleLocale}>
            {copy.language}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            type="button"
            onClick={toggleTheme}
            aria-label={copy.theme}
          >
            <span aria-hidden="true">{theme === "light" ? "◐" : "☀"}</span>
          </Button>
          <Button variant="ghost" size="sm" type="button" onClick={() => void logout()}>
            {copy.signOut}
          </Button>
        </nav>
      </header>
      <Outlet />
    </div>
  );
}
