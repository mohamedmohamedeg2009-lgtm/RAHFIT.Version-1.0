import { Link, Navigate } from "react-router-dom";
import {
  Compass,
  LogIn,
  Dumbbell,
  ShieldCheck,
  Activity,
  ArrowRight,
  ArrowLeft,
} from "lucide-react";

import { PublicHeader } from "../../components/public/PublicHeader";
import { useAuth } from "../../hooks/useAuth";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Card, Badge } from "../../components/ui";

export function LandingPage() {
  const { user, isLoading } = useAuth();
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  useDocumentTitle(locale === "ar" ? "RAHFIT AI — الصفحة الرئيسية" : "RAHFIT AI — Home");
  const ArrowIcon = direction === "rtl" ? ArrowLeft : ArrowRight;

  if (isLoading) {
    return (
      <main className="auth-shell" aria-busy="true" aria-live="polite">
        <div className="loading-card">
          <span className="spinner" aria-hidden="true" />
          <p>Loading experience…</p>
        </div>
      </main>
    );
  }

  if (user) {
    return <Navigate to="/app" replace />;
  }

  return (
    <div className="public-shell" dir={direction}>
      <PublicHeader />

      <main className="public-main-content">
        {/* Landing Hero */}
        <section className="landing-hero" aria-labelledby="landing-hero-title">
          <div className="landing-hero-content">
            <Badge className="discovery-trust-badge">
              <span>{copy.heroTrustBadge}</span>
            </Badge>

            <h1 id="landing-hero-title" className="landing-hero-title">
              {copy.landingHeroTitle}
            </h1>

            <p className="landing-hero-subtitle">{copy.landingHeroSubtitle}</p>

            <div className="landing-hero-actions">
              <Link className="ds-button ds-button-primary ds-button-lg" to="/discover">
                <Compass size={20} />
                <span>{copy.landingHeroCta}</span>
                <ArrowIcon size={18} />
              </Link>

              <Link className="ds-button ds-button-outline ds-button-lg" to="/login">
                <LogIn size={20} />
                <span>{copy.landingLoginCta}</span>
              </Link>
            </div>
          </div>
        </section>

        {/* Landing Value Pillars */}
        <section id="features" className="discovery-section" aria-labelledby="landing-value-title">
          <div className="discovery-section-header">
            <h2 id="landing-value-title" className="discovery-section-title">
              {copy.landingValueTitle}
            </h2>
          </div>

          <div className="discovery-features-grid">
            <Card className="discovery-feature-card">
              <div
                className="discovery-feature-icon-wrapper"
                style={{ backgroundColor: "rgba(15, 118, 110, 0.1)" }}
              >
                <Dumbbell size={24} color="var(--color-primary)" />
              </div>
              <h3 className="discovery-feature-title">{copy.landingValue1Title}</h3>
              <p className="discovery-feature-desc">{copy.landingValue1Desc}</p>
            </Card>

            <Card className="discovery-feature-card">
              <div
                className="discovery-feature-icon-wrapper"
                style={{ backgroundColor: "rgba(20, 184, 166, 0.1)" }}
              >
                <ShieldCheck size={24} color="var(--color-accent)" />
              </div>
              <h3 className="discovery-feature-title">{copy.landingValue2Title}</h3>
              <p className="discovery-feature-desc">{copy.landingValue2Desc}</p>
            </Card>

            <Card className="discovery-feature-card">
              <div
                className="discovery-feature-icon-wrapper"
                style={{ backgroundColor: "rgba(34, 197, 94, 0.1)" }}
              >
                <Activity size={24} color="var(--color-success)" />
              </div>
              <h3 className="discovery-feature-title">{copy.landingValue3Title}</h3>
              <p className="discovery-feature-desc">{copy.landingValue3Desc}</p>
            </Card>
          </div>
        </section>

        {/* Banner to Discover */}
        <section className="discovery-section" style={{ paddingTop: 0 }}>
          <Card className="discovery-final-cta-card">
            <h2 className="discovery-final-cta-title">{copy.heroHeading}</h2>
            <p className="discovery-final-cta-subheading">{copy.heroSubheading}</p>

            <div className="discovery-final-cta-actions">
              <Link className="ds-button ds-button-primary ds-button-lg" to="/discover">
                <Compass size={20} />
                <span>{copy.navDiscover}</span>
                <ArrowIcon size={18} />
              </Link>
            </div>
          </Card>
        </section>
      </main>

      <footer className="public-footer">
        <div className="public-footer-inner">
          <p className="public-footer-brand">RAHFIT AI — Intelligent, Safe & Sustainable Fitness</p>
          <p className="public-footer-copy">
            © {new Date().getFullYear()} RAHFIT AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
