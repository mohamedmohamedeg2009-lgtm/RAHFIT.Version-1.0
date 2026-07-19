import { Link, useLocation } from "react-router-dom";
import { Sun, Moon, Globe, Compass } from "lucide-react";

import { Button } from "../ui";
import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { useTheme } from "../../theme";
import { RahafitLogo } from "../common/RahafitLogo";

export function PublicHeader() {
  const { locale, toggleLocale } = useLocale();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const copy = discoveryCopy[locale];

  const isDiscover = location.pathname === "/discover";

  return (
    <header className="public-topbar" aria-label="Public Navigation">
      <div className="public-topbar-inner">
        <Link className="dashboard-brand" to="/" aria-label="Rahafit Home">
          <RahafitLogo size="md" />
        </Link>

        <nav className="public-nav-links" aria-label="Sections">
          <a href="#how-it-works" className="public-nav-link">
            {copy.navHowItWorks}
          </a>
          <a href="#product-areas" className="public-nav-link">
            {copy.navFeatures}
          </a>
          <a href="#safety-section" className="public-nav-link">
            {copy.navSafety}
          </a>
        </nav>

        <div className="public-header-actions">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleLocale}
            aria-label={locale === "ar" ? "English" : "العربية"}
            style={{ display: "flex", alignItems: "center", gap: "6px" }}
          >
            <Globe size={18} />
            <span style={{ fontSize: "14px", fontWeight: 700 }}>
              {locale === "ar" ? "English" : "العربية"}
            </span>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            aria-label="Toggle color theme"
            aria-pressed={theme === "dark"}
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </Button>

          <Link className="ds-button ds-button-ghost ds-button-sm" to="/login">
            {copy.navLogin}
          </Link>

          {!isDiscover ? (
            <Link className="ds-button ds-button-primary ds-button-sm" to="/discover">
              <Compass size={16} />
              <span>{copy.navDiscover}</span>
            </Link>
          ) : (
            <Link className="ds-button ds-button-primary ds-button-sm" to="/register">
              <span>{copy.navRegister}</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
