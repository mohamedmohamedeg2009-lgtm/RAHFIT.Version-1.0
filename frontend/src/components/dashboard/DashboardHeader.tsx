import { Link, NavLink } from "react-router-dom";
import { Brain, Dumbbell, Globe, LayoutDashboard, LogOut, Utensils } from "lucide-react";

import { Button } from "../ui";
import { useLocale } from "../../contexts/LocaleContext";
import { useAuth } from "../../hooks/useAuth";
import { dashboardCopy } from "../../i18n/dashboard";

interface DashboardHeaderProps {
  displayName: string;
  email?: string;
}

export function DashboardHeader({ displayName, email }: DashboardHeaderProps) {
  const { locale, toggleLocale } = useLocale();
  const { logout } = useAuth();
  const copy = dashboardCopy[locale];

  const getInitials = (name: string) => {
    if (!name) return "U";
    return name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <header className="dashboard-topbar">
      <nav className="dashboard-controls" aria-label={copy.dashboard}>
        <Link
          className="ds-button ds-button-ghost ds-button-sm"
          to="/intelligent-workouts"
          style={{ fontWeight: 700 }}
        >
          {locale === "ar" ? "التدريب الذكي" : "Training"}
        </Link>
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleLocale}
          aria-label={copy.language}
          style={{ display: "flex", alignItems: "center", gap: "6px" }}
        >
          <Globe size={18} />
          <span style={{ fontSize: "14px", fontWeight: 700 }}>{copy.language}</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => void logout().catch(() => undefined)}
          aria-label={copy.signOut}
        >
          <LogOut size={18} />
        </Button>
        <div
          className="header-user-info"
          style={{
            marginLeft: locale === "en" ? "12px" : "0",
            marginRight: locale === "ar" ? "12px" : "0",
          }}
        >
          <div className="header-avatar" title={email}>
            {getInitials(displayName)}
          </div>
        </div>
      </nav>
      <nav className="dashboard-mobile-nav" aria-label={copy.dashboard}>
        <NavLink to="/app" end>
          <LayoutDashboard size={19} aria-hidden="true" />
          <span>{locale === "ar" ? "الرئيسية" : "Home"}</span>
        </NavLink>
        <NavLink to="/intelligent-workouts">
          <Dumbbell size={19} aria-hidden="true" />
          <span>{locale === "ar" ? "التدريب" : "Training"}</span>
        </NavLink>
        <NavLink to="/nutrition">
          <Utensils size={19} aria-hidden="true" />
          <span>{locale === "ar" ? "التغذية" : "Nutrition"}</span>
        </NavLink>
        <NavLink to="/ai-coach">
          <Brain size={19} aria-hidden="true" />
          <span>{locale === "ar" ? "المدرب" : "Coach"}</span>
        </NavLink>
      </nav>
    </header>
  );
}
