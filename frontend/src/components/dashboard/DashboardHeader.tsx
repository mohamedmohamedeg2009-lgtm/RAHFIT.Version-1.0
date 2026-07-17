import { Link } from "react-router-dom";

import { Button } from "../ui";
import { useLocale } from "../../contexts/LocaleContext";
import { useAuth } from "../../hooks/useAuth";
import { dashboardCopy } from "../../i18n/dashboard";
import { useTheme } from "../../theme";

interface DashboardHeaderProps {
  displayName: string;
  email?: string;
}

export function DashboardHeader({ displayName, email }: DashboardHeaderProps) {
  const { locale, toggleLocale } = useLocale();
  const { theme, toggleTheme } = useTheme();
  const { logout } = useAuth();
  const copy = dashboardCopy[locale];

  return (
    <>
      <header className="dashboard-topbar">
        <Link className="dashboard-brand" to="/app" aria-label={`${copy.brand} ${copy.dashboard}`}>
          <span className="dashboard-brand-mark" aria-hidden="true">
            R
          </span>
          <span>
            <strong>{copy.brand}</strong>
            <small>{copy.dashboard}</small>
          </span>
        </Link>
        <nav className="dashboard-controls" aria-label={copy.dashboard}>
          <Link className="ds-button ds-button-ghost ds-button-sm" to="/intelligent-workouts">
            Training
          </Link>
          <Button variant="ghost" size="sm" onClick={toggleLocale} aria-label={copy.language}>
            {copy.language}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            aria-label={copy.theme}
            aria-pressed={theme === "dark"}
          >
            <span aria-hidden="true">{theme === "dark" ? "☀" : "◐"}</span>
          </Button>
          <Button variant="ghost" size="sm" onClick={() => void logout().catch(() => undefined)}>
            {copy.signOut}
          </Button>
        </nav>
      </header>
      <header className="dashboard-welcome">
        <div>
          <span className="dashboard-eyebrow">{copy.dashboard}</span>
          <h1>
            {copy.greeting}, <span>{displayName}</span>
          </h1>
          <p>{copy.context}</p>
        </div>
        {email ? <span className="dashboard-account-label">{email}</span> : null}
      </header>
    </>
  );
}
