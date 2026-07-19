import React from "react";
import { Link, Navigate } from "react-router-dom";
import {
  Sparkles,
  ShieldCheck,
  Bot,
  Activity,
  HeartHandshake,
  ArrowRight,
  ArrowLeft,
  Dumbbell,
  Eye,
  CheckCircle2,
} from "lucide-react";

import { HowItWorksSection } from "../../components/discovery/HowItWorksSection";
import { PublicHeader } from "../../components/public/PublicHeader";
import { PublicFooter } from "../../components/public/PublicFooter";
import { HeroPhoneMockup } from "../../components/public/HeroPhoneMockup";
import { useAuth } from "../../hooks/useAuth";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Card, Badge } from "../../components/ui";

export function LandingPage() {
  const { user, isLoading } = useAuth();
  const { locale, direction } = useLocale();
  const isRtl = direction === "rtl";
  const copy = discoveryCopy[locale];
  useDocumentTitle(locale === "ar" ? "Rahafit — الرئيسية" : "Rahafit — Home");
  const ArrowIcon = isRtl ? ArrowLeft : ArrowRight;

  const handleScrollToFeatures = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const elem = document.getElementById("features");
    if (elem) {
      elem.scrollIntoView({ behavior: "smooth" });
    }
  };

  if (isLoading) {
    return (
      <main className="auth-shell flex items-center justify-center min-h-screen" aria-busy="true" aria-live="polite">
        <div className="loading-card text-center p-8">
          <span className="spinner mb-4" aria-hidden="true" />
          <p className="text-slate-300 font-semibold">Loading experience…</p>
        </div>
      </main>
    );
  }

  if (user) {
    return <Navigate to="/app" replace />;
  }

  return (
    <div className="public-shell min-h-screen flex flex-col bg-slate-950 text-slate-100" dir={direction}>
      <PublicHeader />

      <main className="public-main-content flex-1 max-w-7xl w-full mx-auto px-4 py-6 flex flex-col gap-12">
        {/* Main Hero Card Container */}
        <section
          className="landing-hero-card relative rounded-3xl p-6 md:p-10 border border-slate-800/80 bg-slate-900/60 shadow-2xl overflow-hidden"
          aria-labelledby="landing-hero-title"
          style={{
            backgroundImage:
              "radial-gradient(circle at 70% 30%, rgba(20, 184, 166, 0.12) 0%, transparent 60%), radial-gradient(circle at 10% 80%, rgba(245, 158, 11, 0.08) 0%, transparent 50%)",
          }}
        >
          {/* Main 2-Column Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Right Column in RTL: Hero Copy & Actions */}
            <div className="lg:col-span-7 flex flex-col gap-5 text-start z-10">
              {/* Trust Badge */}
              <div>
                <Badge className="discovery-trust-badge inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-xs font-bold">
                  <Sparkles size={14} className="text-amber-400" />
                  <span>{copy.heroTrustBadge}</span>
                </Badge>
              </div>

              {/* Main Headline */}
              <h1
                id="landing-hero-title"
                className="landing-hero-title text-3xl sm:text-4xl md:text-5xl font-black tracking-tight leading-tight text-white"
              >
                {copy.landingHeroHeadline}
              </h1>

              {/* Supporting Subheading */}
              <p className="landing-hero-subtitle text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
                {copy.landingHeroSubheading}
              </p>

              {/* 3-Tier CTA Hierarchy */}
              <div className="landing-hero-actions flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2">
                {/* Primary Gold CTA */}
                <Link
                  className="ds-button ds-button-primary ds-button-lg bg-amber-500 hover:bg-amber-600 text-slate-950 font-extrabold px-6 py-3.5 rounded-xl shadow-lg shadow-amber-500/20 flex items-center justify-center gap-2.5 transition-all text-base"
                  to="/register"
                >
                  <Sparkles size={18} />
                  <span>{copy.landingHeroPrimaryCta}</span>
                  <ArrowIcon size={18} />
                </Link>

                {/* Secondary Teal Outline CTA */}
                <a
                  className="ds-button ds-button-outline ds-button-lg border border-teal-500/40 hover:border-teal-400 text-teal-300 hover:bg-teal-500/10 font-bold px-6 py-3.5 rounded-xl flex items-center justify-center gap-2.5 transition-all text-base"
                  href="#features"
                  onClick={handleScrollToFeatures}
                >
                  <Eye size={18} />
                  <span>{copy.landingHeroSecondaryCta}</span>
                </a>
              </div>

              {/* Tertiary Login Link */}
              <div className="pt-1">
                <Link
                  to="/login"
                  className="text-xs text-slate-400 hover:text-amber-400 underline underline-offset-4 transition-colors font-medium"
                >
                  {copy.landingHeroTertiaryCta}
                </Link>
              </div>
            </div>

            {/* Left Column in RTL: Phone Mockup Container */}
            <div className="lg:col-span-5 flex justify-center items-center z-10">
              <HeroPhoneMockup />
            </div>
          </div>

          {/* Four Bottom Value Items */}
          <div className="hero-value-pillars border-t border-slate-800/80 mt-10 pt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 z-10 relative">
            {/* Value Item 1: Secure & Trusted */}
            <div className="value-item-card flex items-start gap-3.5 p-3 rounded-2xl bg-slate-950/40 border border-slate-800/60 hover:border-teal-500/30 transition-all">
              <div className="icon-wrapper shrink-0 w-10 h-10 rounded-full bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
                <ShieldCheck size={20} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white mb-0.5">{copy.valueItem1Title}</h3>
                <p className="text-xs text-slate-400 leading-snug">{copy.valueItem1Desc}</p>
              </div>
            </div>

            {/* Value Item 2: Personalized AI */}
            <div className="value-item-card flex items-start gap-3.5 p-3 rounded-2xl bg-slate-950/40 border border-slate-800/60 hover:border-teal-500/30 transition-all">
              <div className="icon-wrapper shrink-0 w-10 h-10 rounded-full bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
                <Bot size={20} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white mb-0.5">{copy.valueItem2Title}</h3>
                <p className="text-xs text-slate-400 leading-snug">{copy.valueItem2Desc}</p>
              </div>
            </div>

            {/* Value Item 3: Comprehensive Tracking */}
            <div className="value-item-card flex items-start gap-3.5 p-3 rounded-2xl bg-slate-950/40 border border-slate-800/60 hover:border-teal-500/30 transition-all">
              <div className="icon-wrapper shrink-0 w-10 h-10 rounded-full bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
                <Activity size={20} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white mb-0.5">{copy.valueItem3Title}</h3>
                <p className="text-xs text-slate-400 leading-snug">{copy.valueItem3Desc}</p>
              </div>
            </div>

            {/* Value Item 4: Continuous Support */}
            <div className="value-item-card flex items-start gap-3.5 p-3 rounded-2xl bg-slate-950/40 border border-slate-800/60 hover:border-teal-500/30 transition-all">
              <div className="icon-wrapper shrink-0 w-10 h-10 rounded-full bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
                <HeartHandshake size={20} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white mb-0.5">{copy.valueItem4Title}</h3>
                <p className="text-xs text-slate-400 leading-snug">{copy.valueItem4Desc}</p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <HowItWorksSection />

        {/* Features Grid Section */}
        <section id="features" className="discovery-section py-8" aria-labelledby="landing-value-title">
          <div className="text-center mb-8">
            <h2 id="landing-value-title" className="text-2xl sm:text-3xl font-extrabold text-white mb-2">
              {copy.productAreasHeading}
            </h2>
            <p className="text-slate-400 text-sm max-w-2xl mx-auto">{copy.productAreasSubheading}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-6 bg-slate-900/40 border-slate-800 flex flex-col gap-3">
              <div className="w-12 h-12 rounded-xl bg-teal-500/10 text-teal-400 flex items-center justify-center">
                <Dumbbell size={24} />
              </div>
              <h3 className="font-bold text-lg text-white">{copy.featureWorkoutTitle}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{copy.featureWorkoutDesc}</p>
            </Card>

            <Card className="p-6 bg-slate-900/40 border-slate-800 flex flex-col gap-3">
              <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
                <ShieldCheck size={24} />
              </div>
              <h3 className="font-bold text-lg text-white">{copy.featureAssessmentTitle}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{copy.featureAssessmentDesc}</p>
            </Card>

            <Card className="p-6 bg-slate-900/40 border-slate-800 flex flex-col gap-3">
              <div className="w-12 h-12 rounded-xl bg-teal-500/10 text-teal-400 flex items-center justify-center">
                <Bot size={24} />
              </div>
              <h3 className="font-bold text-lg text-white">{copy.featureAiCoachTitle}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{copy.featureAiCoachDesc}</p>
            </Card>
          </div>
        </section>

        {/* Safety & Privacy Section */}
        <section id="safety-section" className="discovery-section py-8" aria-labelledby="safety-title">
          <Card className="p-8 bg-slate-900/60 border-teal-500/20">
            <div className="flex items-center gap-3 mb-4 text-teal-400">
              <ShieldCheck size={28} />
              <h2 id="safety-title" className="text-xl sm:text-2xl font-extrabold text-white">
                {copy.safetyHeading}
              </h2>
            </div>
            <p className="text-sm text-slate-300 mb-6">{copy.safetySubheading}</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="flex flex-col gap-1.5">
                <h3 className="font-bold text-sm text-white flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-teal-400" />
                  {copy.safetyPoint1Title}
                </h3>
                <p className="text-xs text-slate-400">{copy.safetyPoint1Desc}</p>
              </div>

              <div className="flex flex-col gap-1.5">
                <h3 className="font-bold text-sm text-white flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-teal-400" />
                  {copy.safetyPoint2Title}
                </h3>
                <p className="text-xs text-slate-400">{copy.safetyPoint2Desc}</p>
              </div>

              <div className="flex flex-col gap-1.5">
                <h3 className="font-bold text-sm text-white flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-teal-400" />
                  {copy.safetyPoint3Title}
                </h3>
                <p className="text-xs text-slate-400">{copy.safetyPoint3Desc}</p>
              </div>
            </div>
          </Card>
        </section>

        {/* Pricing Section Placeholder */}
        <section id="pricing" className="discovery-section py-8" aria-labelledby="pricing-title">
          <div className="text-center mb-8">
            <h2 id="pricing-title" className="text-2xl sm:text-3xl font-extrabold text-white mb-2">
              {copy.pricingHeading}
            </h2>
            <p className="text-slate-400 text-sm max-w-2xl mx-auto">{copy.pricingSubheading}</p>
          </div>

          <Card className="max-w-md mx-auto p-6 bg-slate-900/60 border-amber-500/30 text-center flex flex-col gap-4">
            <Badge className="self-center bg-amber-500/10 text-amber-400 border-amber-500/20 px-3 py-1 font-bold text-xs">
              {copy.pricingFreeTitle}
            </Badge>
            <h3 className="text-2xl font-black text-white">{isRtl ? "مجاني بالكامل" : "100% Free"}</h3>
            <p className="text-xs text-slate-300">{copy.pricingFreeDesc}</p>
            <Link
              to="/register"
              className="ds-button ds-button-primary bg-amber-500 hover:bg-amber-600 text-slate-950 font-extrabold py-3 rounded-xl shadow-lg"
            >
              {copy.landingHeroPrimaryCta}
            </Link>
          </Card>
        </section>

        {/* Final CTA Banner */}
        <section className="discovery-section pb-8">
          <Card className="p-8 md:p-12 bg-gradient-to-r from-slate-900 via-teal-950/40 to-slate-900 border-teal-500/30 text-center flex flex-col items-center gap-4">
            <h2 className="text-2xl sm:text-4xl font-black text-white">{copy.finalCtaHeading}</h2>
            <p className="text-sm sm:text-base text-slate-300 max-w-xl">{copy.finalCtaSubheading}</p>
            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <Link
                className="ds-button ds-button-primary bg-amber-500 hover:bg-amber-600 text-slate-950 font-extrabold px-8 py-3.5 rounded-xl shadow-lg"
                to="/register"
              >
                <span>{copy.finalCtaPrimary}</span>
              </Link>
              <Link
                className="ds-button ds-button-outline border-slate-700 text-slate-300 hover:bg-slate-800 px-6 py-3.5 rounded-xl font-bold"
                to="/login"
              >
                <span>{copy.finalCtaSecondary}</span>
              </Link>
            </div>
          </Card>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}

export default LandingPage;
