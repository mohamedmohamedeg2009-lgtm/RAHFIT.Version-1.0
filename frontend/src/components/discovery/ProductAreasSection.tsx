import { Link } from "react-router-dom";
import {
  Dumbbell,
  ShieldCheck,
  Bot,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Check,
} from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Badge } from "../ui";

export function ProductAreasSection() {
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  const isRtl = direction === "rtl";
  const ArrowIcon = isRtl ? ArrowLeft : ArrowRight;

  return (
    <section
      id="features"
      className="features-section relative py-12 px-4 max-w-7xl mx-auto rounded-3xl bg-slate-900/40 border border-slate-800/80 overflow-hidden"
      aria-labelledby="features-title"
    >
      {/* Soft Background Radial Glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(circle at 70% 20%, rgba(20, 184, 166, 0.08) 0%, transparent 65%), radial-gradient(circle at 20% 80%, rgba(245, 158, 11, 0.06) 0%, transparent 60%)",
        }}
        aria-hidden="true"
      />

      {/* 1. Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-12 relative z-10">
        <Badge className="inline-flex items-center gap-1.5 px-3 py-1 mb-3 bg-teal-500/10 border border-teal-500/20 text-teal-400 font-extrabold text-xs tracking-wider rounded-full uppercase">
          <Sparkles size={12} className="text-amber-400" />
          <span>{copy.featuresEyebrow}</span>
        </Badge>

        <h2
          id="features-title"
          className="text-2xl sm:text-3xl md:text-4xl font-black text-white tracking-tight mb-3"
        >
          {copy.featuresHeading}
        </h2>

        <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-normal">
          {copy.featuresSubheading}
        </p>
      </div>

      {/* 2. Asymmetric Showcase Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 relative z-10">
        {/* DOMINANT FEATURED CARD: Intelligent Workout Guidance */}
        <article className="featured-product-card lg:col-span-7 flex flex-col justify-between p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-slate-950/80 via-slate-900/90 to-teal-950/40 border border-teal-500/30 hover:border-teal-500/50 transition-all duration-300 shadow-xl shadow-teal-950/20 group">
          <div>
            {/* Header: Icon & Badge */}
            <div className="flex items-center justify-between mb-6">
              <div className="w-14 h-14 rounded-2xl bg-teal-500/10 border border-teal-500/30 text-teal-400 flex items-center justify-center shadow-[0_0_20px_rgba(20,184,166,0.2)] group-hover:scale-105 transition-transform">
                <Dumbbell size={28} />
              </div>

              <Badge className="bg-amber-500/10 border border-amber-500/30 text-amber-400 font-bold text-xs px-3 py-1 rounded-full">
                <Sparkles size={12} className="mr-1" />
                <span>{copy.featureWorkoutBadge}</span>
              </Badge>
            </div>

            {/* Title & Description */}
            <h3 className="text-xl sm:text-2xl font-black text-white mb-3 group-hover:text-teal-300 transition-colors">
              {copy.featureWorkoutTitle}
            </h3>

            <p className="text-sm text-slate-300 leading-relaxed mb-6">
              {copy.featureWorkoutDesc}
            </p>

            {/* 3 Supporting Bullet Points */}
            <div className="flex flex-col gap-2.5 mb-8 pt-4 border-t border-slate-800/80">
              <div className="flex items-center gap-2.5 text-xs sm:text-sm font-semibold text-slate-200">
                <div className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-400 flex items-center justify-center shrink-0">
                  <Check size={12} strokeWidth={3} />
                </div>
                <span>{copy.featureWorkoutPoint1}</span>
              </div>

              <div className="flex items-center gap-2.5 text-xs sm:text-sm font-semibold text-slate-200">
                <div className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-400 flex items-center justify-center shrink-0">
                  <Check size={12} strokeWidth={3} />
                </div>
                <span>{copy.featureWorkoutPoint2}</span>
              </div>

              <div className="flex items-center gap-2.5 text-xs sm:text-sm font-semibold text-slate-200">
                <div className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-400 flex items-center justify-center shrink-0">
                  <Check size={12} strokeWidth={3} />
                </div>
                <span>{copy.featureWorkoutPoint3}</span>
              </div>
            </div>
          </div>

          {/* Primary CTA */}
          <div>
            <Link
              to="/register"
              className="ds-button ds-button-primary bg-teal-500 hover:bg-teal-600 text-slate-950 font-extrabold px-6 py-3 rounded-xl shadow-lg shadow-teal-500/20 inline-flex items-center gap-2 transition-all text-sm w-full sm:w-auto justify-center"
            >
              <span>{copy.featureWorkoutCta}</span>
              <ArrowIcon size={16} />
            </Link>
          </div>
        </article>

        {/* SUPPORTING CARDS STACK */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          {/* Supporting Card 1: Smart Assessment */}
          <article className="supporting-product-card p-6 rounded-3xl bg-slate-950/70 border border-amber-500/30 hover:border-amber-500/50 transition-all duration-300 shadow-lg group">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center shadow-[0_0_15px_rgba(245,158,11,0.15)] group-hover:scale-105 transition-transform">
                <ShieldCheck size={24} />
              </div>

              <Badge className="bg-amber-500/10 border border-amber-500/20 text-amber-400 font-bold text-xs px-2.5 py-1 rounded-full">
                <span>{copy.featureAssessmentBadge}</span>
              </Badge>
            </div>

            <h3 className="text-lg font-bold text-white mb-2 group-hover:text-amber-300 transition-colors">
              {copy.featureAssessmentTitle}
            </h3>

            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              {copy.featureAssessmentDesc}
            </p>

            {/* Illustrative Readiness Bar */}
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={16} className="text-amber-400 shrink-0" />
                <span className="text-xs font-semibold text-slate-200">
                  {isRtl ? "جاهزية صحية مكتملة 100%" : "100% Health Clearance"}
                </span>
              </div>
              <span className="text-[10px] font-extrabold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded">
                SAFE
              </span>
            </div>
          </article>

          {/* Supporting Card 2: AI Coach */}
          <article className="supporting-product-card p-6 rounded-3xl bg-slate-950/70 border border-teal-500/20 hover:border-teal-500/40 transition-all duration-300 shadow-lg group">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/30 text-teal-400 flex items-center justify-center shadow-[0_0_15px_rgba(20,184,166,0.15)] group-hover:scale-105 transition-transform">
                <Bot size={24} />
              </div>

              <Badge className="bg-teal-500/10 border border-teal-500/20 text-teal-400 font-bold text-xs px-2.5 py-1 rounded-full">
                <span>{copy.featureAiCoachBadge}</span>
              </Badge>
            </div>

            <h3 className="text-lg font-bold text-white mb-2 group-hover:text-teal-300 transition-colors">
              {copy.featureAiCoachTitle}
            </h3>

            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              {copy.featureAiCoachDesc}
            </p>

            {/* Topic Chips */}
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="text-[11px] font-semibold text-teal-300 bg-teal-500/10 border border-teal-500/20 px-2.5 py-1 rounded-full">
                {copy.featureAiChip1}
              </span>
              <span className="text-[11px] font-semibold text-amber-300 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-full">
                {copy.featureAiChip2}
              </span>
              <span className="text-[11px] font-semibold text-teal-300 bg-teal-500/10 border border-teal-500/20 px-2.5 py-1 rounded-full">
                {copy.featureAiChip3}
              </span>
            </div>

            {/* Non-Medical Disclaimer Note */}
            <p className="text-[10px] text-slate-400 leading-tight">
              {copy.featureAiDisclaimer}
            </p>
          </article>
        </div>
      </div>
    </section>
  );
}
