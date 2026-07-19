import React from "react";
import { Link } from "react-router-dom";
import { Globe } from "lucide-react";

import { Button } from "../ui";
import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { RahafitLogo } from "../common/RahafitLogo";

export function PublicHeader() {
  const { locale, toggleLocale } = useLocale();
  const copy = discoveryCopy[locale];

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, targetId: string) => {
    const elem = document.getElementById(targetId);
    if (elem) {
      e.preventDefault();
      elem.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <header
      className="public-topbar sticky top-0 z-50 backdrop-blur-md"
      aria-label="Public Navigation"
    >
      <div className="public-topbar-inner flex items-center justify-between max-w-7xl mx-auto px-4 py-3">
        {/* Brand Logo (Far right in RTL, Far left in LTR) */}
        <Link className="dashboard-brand flex items-center gap-2" to="/" aria-label="Rahafit Home">
          <RahafitLogo size="md" />
        </Link>

        {/* Navigation Links */}
        <nav className="public-nav-links hidden md:flex items-center gap-6" aria-label="Sections">
          <a
            href="#how-it-works"
            className="public-nav-link text-sm font-semibold transition-colors hover:text-teal-400"
            onClick={(e) => handleNavClick(e, "how-it-works")}
          >
            {copy.navHowItWorks}
          </a>
          <a
            href="#features"
            className="public-nav-link text-sm font-semibold transition-colors hover:text-teal-400"
            onClick={(e) => handleNavClick(e, "features")}
          >
            {copy.navFeatures}
          </a>
          <a
            href="#safety-section"
            className="public-nav-link text-sm font-semibold transition-colors hover:text-teal-400"
            onClick={(e) => handleNavClick(e, "safety-section")}
          >
            {copy.navSafety}
          </a>
          <a
            href="#pricing"
            className="public-nav-link text-sm font-semibold transition-colors hover:text-teal-400"
            onClick={(e) => handleNavClick(e, "pricing")}
          >
            {copy.navPricing}
          </a>
        </nav>

        {/* Action Controls */}
        <div className="public-header-actions flex items-center gap-2">
          {/* Language Switcher */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleLocale}
            aria-label={locale === "ar" ? "Switch to English" : "التحويل للعربية"}
            className="flex items-center gap-1.5 text-xs font-bold px-2.5 py-1.5"
          >
            <Globe size={16} />
            <span>{locale === "ar" ? "English" : "العربية"}</span>
          </Button>

          {/* Sign In Link */}
          <Link
            className="ds-button ds-button-ghost ds-button-sm text-xs font-bold px-3 py-1.5"
            to="/login"
          >
            {copy.navLogin}
          </Link>

          {/* Primary Gold Create Account Button */}
          <Link
            className="ds-button ds-button-primary ds-button-sm text-xs font-bold px-4 py-1.5 bg-amber-500 hover:bg-amber-600 text-slate-950 rounded-lg shadow-sm font-extrabold transition-all"
            to="/register"
          >
            <span>{copy.navRegister}</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
