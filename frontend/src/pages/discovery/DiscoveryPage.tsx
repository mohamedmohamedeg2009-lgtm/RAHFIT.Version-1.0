import { PublicHeader } from "../../components/public/PublicHeader";
import { PublicFooter } from "../../components/public/PublicFooter";
import { HeroSection } from "../../components/discovery/HeroSection";
import { HowItWorksSection } from "../../components/discovery/HowItWorksSection";
import { ProductAreasSection } from "../../components/discovery/ProductAreasSection";
import { DashboardPreviewSection } from "../../components/discovery/DashboardPreviewSection";
import { AiCoachShowcaseSection } from "../../components/discovery/AiCoachShowcaseSection";
import { SafetySection } from "../../components/discovery/SafetySection";
import { TrustMetricsSection } from "../../components/discovery/TrustMetricsSection";
import { ProductScopeSection } from "../../components/discovery/ProductScopeSection";
import { PricingSection } from "../../components/discovery/PricingSection";
import { FinalCtaSection } from "../../components/discovery/FinalCtaSection";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { useLocale } from "../../contexts/LocaleContext";

export function DiscoveryPage() {
  const { locale } = useLocale();
  useDocumentTitle(locale === "ar" ? "استكشف Rahafit" : "Discover Rahafit");

  return (
    <div
      className="public-shell min-h-screen flex flex-col bg-slate-950 text-slate-100"
      dir={locale === "ar" ? "rtl" : "ltr"}
    >
      <PublicHeader />
      <main className="public-main-content flex-1 max-w-7xl w-full mx-auto px-4 py-6 flex flex-col gap-12">
        <HeroSection />
        <HowItWorksSection />
        <ProductAreasSection />
        <DashboardPreviewSection />
        <AiCoachShowcaseSection />
        <SafetySection />
        <TrustMetricsSection />
        <ProductScopeSection />
        <PricingSection />
        <FinalCtaSection />
      </main>
      <PublicFooter />
    </div>
  );
}

export default DiscoveryPage;
