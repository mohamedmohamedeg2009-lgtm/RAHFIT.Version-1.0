import React from "react";
import { Link } from "react-router-dom";
import {
  UserPlus,
  Target,
  Sparkles,
  Activity,
  ArrowRight,
  ArrowLeft,
  ChevronDown,
} from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Badge } from "../ui";

export function HowItWorksSection() {
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  const isRtl = direction === "rtl";
  const ArrowIcon = isRtl ? ArrowLeft : ArrowRight;

  const handleScrollToFeatures = (e: React.MouseEvent<HTMLAnchorElement>) => {
    const elem = document.getElementById("features");
    if (elem) {
      e.preventDefault();
      elem.scrollIntoView({ behavior: "smooth" });
    }
  };

  const steps = [
    {
      number: "01",
      icon: UserPlus,
      title: copy.step1Title,
      desc: copy.step1Desc,
      accent: "teal",
    },
    {
      number: "02",
      icon: Target,
      title: copy.step2Title,
      desc: copy.step2Desc,
      accent: "gold",
    },
    {
      number: "03",
      icon: Sparkles,
      title: copy.step3Title,
      desc: copy.step3Desc,
      accent: "teal",
    },
    {
      number: "04",
      icon: Activity,
      title: copy.step4Title,
      desc: copy.step4Desc,
      accent: "gold",
    },
  ];

  return (
    <section
      id="how-it-works"
      className="how-it-works-section relative py-12 px-4 max-w-7xl mx-auto rounded-3xl bg-slate-900/40 border border-slate-800/80 overflow-hidden"
      aria-labelledby="how-it-works-title"
    >
      {/* Background Soft Radial Glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(circle at 50% 30%, rgba(20, 184, 166, 0.08) 0%, transparent 70%)",
        }}
        aria-hidden="true"
      />

      {/* 1. Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-12 relative z-10">
        <Badge className="inline-flex items-center gap-1.5 px-3 py-1 mb-3 bg-teal-500/10 border border-teal-500/20 text-teal-400 font-extrabold text-xs tracking-wider rounded-full uppercase">
          <Sparkles size={12} className="text-amber-400" />
          <span>{copy.howItWorksEyebrow}</span>
        </Badge>

        <h2
          id="how-it-works-title"
          className="text-2xl sm:text-3xl md:text-4xl font-black text-white tracking-tight mb-3"
        >
          {copy.howItWorksHeading}
        </h2>

        <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-normal">
          {copy.howItWorksSubheading}
        </p>
      </div>

      {/* 2. Connected Timeline Container */}
      <div className="relative z-10 mb-12">
        {/* Desktop Horizontal Progress Connecting Line (Hidden on Mobile) */}
        <div
          className="hidden lg:block absolute top-12 left-16 right-16 h-1 bg-gradient-to-r from-teal-500/30 via-amber-500/40 to-teal-500/30 rounded-full"
          aria-hidden="true"
        />

        {/* Mobile Vertical Progress Connecting Line (Hidden on Desktop) */}
        <div
          className={`lg:hidden absolute top-6 bottom-6 ${
            isRtl ? "right-8" : "left-8"
          } w-1 bg-gradient-to-b from-teal-500/40 via-amber-500/40 to-teal-500/40 rounded-full`}
          aria-hidden="true"
        />

        {/* Semantic Ordered Steps List */}
        <ol className="grid grid-cols-1 lg:grid-cols-4 gap-6 relative">
          {steps.map((step) => {
            const Icon = step.icon;
            const isGold = step.accent === "gold";

            return (
              <li
                key={step.number}
                className="step-timeline-card relative group flex flex-col p-6 rounded-2xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition-all duration-300 hover:-translate-y-1 shadow-lg"
              >
                {/* Step Header: Large Number & Icon Container */}
                <div className="flex items-center justify-between mb-4 z-10">
                  {/* Icon Node Container */}
                  <div
                    className={`w-12 h-12 rounded-2xl flex items-center justify-center border transition-transform duration-300 group-hover:scale-105 ${
                      isGold
                        ? "bg-amber-500/10 border-amber-500/30 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.15)]"
                        : "bg-teal-500/10 border-teal-500/30 text-teal-400 shadow-[0_0_15px_rgba(20,184,166,0.15)]"
                    }`}
                  >
                    <Icon size={22} />
                  </div>

                  {/* Large Step Number Badge */}
                  <span
                    className={`text-2xl font-black tracking-tight ${
                      isGold ? "text-amber-400/90" : "text-teal-400/90"
                    }`}
                  >
                    {step.number}
                  </span>
                </div>

                {/* Step Text Content */}
                <div className="flex flex-col gap-1.5 z-10">
                  <h3 className="text-base font-bold text-white group-hover:text-amber-300 transition-colors">
                    {step.title}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed font-normal">
                    {step.desc}
                  </p>
                </div>
              </li>
            );
          })}
        </ol>
      </div>

      {/* 3. Compact CTA Row Below Timeline */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 relative z-10 pt-2 border-t border-slate-800/60">
        {/* Primary Gold CTA */}
        <Link
          to="/register"
          className="ds-button ds-button-primary bg-amber-500 hover:bg-amber-600 text-slate-950 font-extrabold px-6 py-3 rounded-xl shadow-lg shadow-amber-500/20 flex items-center gap-2 transition-all text-sm w-full sm:w-auto justify-center"
        >
          <span>{copy.howItWorksPrimaryCta}</span>
          <ArrowIcon size={16} />
        </Link>

        {/* Secondary Teal Outline CTA */}
        <a
          href="#features"
          onClick={handleScrollToFeatures}
          className="ds-button ds-button-outline border border-teal-500/40 text-teal-300 hover:bg-teal-500/10 font-bold px-6 py-3 rounded-xl flex items-center gap-2 transition-all text-sm w-full sm:w-auto justify-center"
        >
          <span>{copy.howItWorksSecondaryCta}</span>
          <ChevronDown size={16} />
        </a>
      </div>
    </section>
  );
}
