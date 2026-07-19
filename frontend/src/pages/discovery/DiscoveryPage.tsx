import { PublicHeader } from "../../components/public/PublicHeader";
import { PublicFooter } from "../../components/public/PublicFooter";
import { HeroSection } from "../../components/discovery/HeroSection";
import { HowItWorksSection } from "../../components/discovery/HowItWorksSection";
import { ProductAreasSection } from "../../components/discovery/ProductAreasSection";
import { SafetySection } from "../../components/discovery/SafetySection";
import { FinalCtaSection } from "../../components/discovery/FinalCtaSection";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { useLocale } from "../../contexts/LocaleContext";

export function DiscoveryPage() {
  const { locale } = useLocale();
  useDocumentTitle(locale === "ar" ? "استكشف Rahafit" : "Discover Rahafit");

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
      <PublicFooter />
    </div>
  );
}

export default DiscoveryPage;
