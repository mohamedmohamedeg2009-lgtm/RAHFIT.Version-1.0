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

  const renderHeadingText = (heading: string) => {
    const parts = heading.split("Rahafit");
    if (parts.length > 1) {
      return (
        <>
          {parts[0]}
          <span className="heading-accent-text">Rahafit</span>
          {parts[1]}
        </>
      );
    }

    return heading;
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
      className="how-it-works-section relative overflow-hidden py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto rounded-[2rem] border border-slate-200/80 shadow-[0_40px_120px_rgba(15,23,42,0.08)]"
      aria-labelledby="how-it-works-title"
    >
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(20,184,166,0.18),_transparent_38%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,_rgba(14,165,233,0.14),_transparent_34%)]" />
        <div className="absolute left-8 top-10 h-32 w-32 rounded-full bg-amber-400/10 blur-3xl" />
        <div className="absolute right-10 bottom-12 h-36 w-36 rounded-full bg-sky-400/10 blur-3xl" />
        <div className="absolute inset-0 opacity-[0.45] [background-image:linear-gradient(rgba(15,23,42,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(15,23,42,0.04)_1px,transparent_1px)] [background-size:36px_36px]" />
      </div>

      <div className="text-center max-w-3xl mx-auto mb-12 relative z-10">
        <Badge className="section-badge inline-flex items-center gap-2 px-3.5 py-2 mb-5 rounded-full border border-white/60 text-[11px] font-black tracking-[0.24em] uppercase shadow-[0_10px_30px_rgba(15,23,42,0.08)] backdrop-blur-xl">
          <Sparkles size={12} className="text-amber-500" />
          <span>{copy.howItWorksEyebrow}</span>
        </Badge>

        <h2
          id="how-it-works-title"
          className="section-title text-3xl sm:text-4xl lg:text-5xl font-black tracking-[-0.03em] mb-4 leading-[0.95]"
        >
          {renderHeadingText(copy.howItWorksHeading)}
        </h2>

        <p className="section-subtitle text-base sm:text-lg leading-8 font-medium max-w-2xl mx-auto">
          {copy.howItWorksSubheading}
        </p>
      </div>

      <div className="relative z-10 mb-12">
        <div className="timeline-connector hidden lg:block absolute top-16 left-[8%] right-[8%] h-[2px] rounded-full" aria-hidden="true" />
        <div className="timeline-connector-mobile lg:hidden absolute top-8 bottom-8 left-8 w-[2px] rounded-full" aria-hidden="true" />

        <ol className="grid grid-cols-1 lg:grid-cols-4 gap-5 lg:gap-6 relative">
          {steps.map((step) => {
            const Icon = step.icon;
            const isGold = step.accent === "gold";

            return (
              <li
                key={step.number}
                className="step-timeline-card relative group flex flex-col p-6 sm:p-7 rounded-[1.6rem] border border-slate-200/80 bg-white/90 backdrop-blur-xl transition-all duration-300 hover:-translate-y-2"
              >
                <div className="flex items-center justify-between mb-6 z-10">
                  <div
                    className={`step-icon-wrapper flex h-13 w-13 items-center justify-center rounded-[1.15rem] border transition-all duration-300 group-hover:scale-110 ${
                      isGold
                        ? "bg-amber-500/12 border-amber-500/30 text-amber-600"
                        : "bg-teal-500/12 border-teal-500/30 text-teal-600"
                    }`}
                  >
                    <Icon size={22} />
                  </div>

                  <span
                    className={`step-number text-2xl font-black tracking-[-0.03em] ${
                      isGold ? "text-amber-500" : "text-teal-600"
                    }`}
                  >
                    {step.number}
                  </span>
                </div>

                <div className="flex flex-col gap-2 z-10">
                  <h3 className="step-title text-lg font-black tracking-[-0.02em]">
                    {step.title}
                  </h3>
                  <p className="step-desc text-sm sm:text-[15px] leading-7 font-medium">
                    {step.desc}
                  </p>
                </div>

                <div className="mt-6 h-1.5 w-20 rounded-full bg-gradient-to-r from-teal-500/40 via-sky-500/40 to-amber-500/50" />
                <div className="timeline-node absolute hidden lg:block" aria-hidden="true" />
              </li>
            );
          })}
        </ol>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 relative z-10 pt-6 border-t border-slate-200/80">
        <Link
          to="/register"
          className="cta-primary ds-button ds-button-primary flex w-full sm:w-auto items-center justify-center gap-2 rounded-full px-7 py-3.5 text-sm font-black shadow-[0_18px_40px_rgba(14,165,233,0.25)] transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_24px_55px_rgba(14,165,233,0.28)]"
        >
          <span>{copy.howItWorksPrimaryCta}</span>
          <ArrowIcon size={16} />
        </Link>

        <a
          href="#features"
          onClick={handleScrollToFeatures}
          className="cta-secondary ds-button ds-button-outline flex w-full sm:w-auto items-center justify-center gap-2 rounded-full border border-slate-300/90 px-7 py-3.5 text-sm font-bold transition-all duration-300 hover:-translate-y-0.5 hover:bg-slate-50"
        >
          <span>{copy.howItWorksSecondaryCta}</span>
          <ChevronDown size={16} />
        </a>
      </div>
    </section>
  );
}
