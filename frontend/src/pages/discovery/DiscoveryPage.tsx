import { PublicHeader } from "../../components/public/PublicHeader";
import { HeroSection } from "../../components/discovery/HeroSection";
import { HowItWorksSection } from "../../components/discovery/HowItWorksSection";
import { ProductAreasSection } from "../../components/discovery/ProductAreasSection";
import { SafetySection } from "../../components/discovery/SafetySection";
import { FinalCtaSection } from "../../components/discovery/FinalCtaSection";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { useLocale } from "../../contexts/LocaleContext";

export function DiscoveryPage() {
  const { locale } = useLocale();
  useDocumentTitle(locale === "ar" ? "استكشف Rahfit | RAHFIT AI" : "Discover Rahfit | RAHFIT AI");

  return (
    <div className="public-shell" dir={locale === "ar" ? "rtl" : "ltr"}>
      <PublicHeader />
      <main className="public-main-content">
        <HeroSection />
        <HowItWorksSection />
        <ProductAreasSection />
        <SafetySection />
        <FinalCtaSection />
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

export default DiscoveryPage;
