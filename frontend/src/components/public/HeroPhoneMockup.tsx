import React from "react";
import {
  Dumbbell,
  Droplets,
  Moon,
  Heart,
  Bot,
  Send,
  Target,
  Sparkles,
  CheckCircle2,
  Home,
  Zap,
} from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { RahafitLogo } from "../common/RahafitLogo";
import { HeroFloatingCard } from "./HeroFloatingCard";

export const HeroPhoneMockup: React.FC = () => {
  const { locale } = useLocale();
  const copy = discoveryCopy[locale];
  const isRtl = locale === "ar";

  return (
    <div
      className="hero-mockup-wrapper relative flex justify-center items-center py-4"
      aria-label="Rahafit App Demo Interface"
    >
      {/* Decorative Teal Orbit Line behind Phone */}
      <div
        className="hero-orbit-line absolute pointer-events-none rounded-full border border-teal-500/20 shadow-[0_0_50px_rgba(20,184,166,0.15)]"
        style={{
          width: "380px",
          height: "380px",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%) rotate(-15deg)",
          zIndex: 0,
        }}
        aria-hidden="true"
      />

      {/* Gold Sparkle Accent */}
      <div
        className="hero-sparkle-accent absolute text-amber-400 pointer-events-none animate-pulse"
        style={{ top: "8%", right: "12%", zIndex: 2 }}
        aria-hidden="true"
      >
        <Sparkles size={20} />
      </div>

      {/* Smartphone Frame Container with counter-clockwise desktop tilt */}
      <div
        className="hero-phone-frame relative z-10 w-[300px] sm:w-[320px] bg-slate-950 rounded-[44px] p-3 shadow-2xl border-4 border-slate-800/80 transition-transform duration-300 hover:rotate-0"
        style={{ transform: "rotate(-4deg)" }}
      >
        {/* Dynamic Island / Notch */}
        <div className="hero-phone-notch flex items-center justify-center gap-2 bg-slate-900 rounded-full w-28 h-5 mx-auto mb-2">
          <div className="hero-phone-camera w-2.5 h-2.5 rounded-full bg-slate-950" />
          <div className="hero-phone-speaker w-8 h-1.5 rounded-full bg-slate-950" />
        </div>

        {/* Screen inner UI */}
        <div
          className="hero-phone-screen bg-slate-900 rounded-[32px] p-3 text-slate-100 flex flex-col gap-2.5 border border-slate-800/60 overflow-hidden"
          dir={isRtl ? "rtl" : "ltr"}
        >
          {/* Header Bar with Rahafit Logo */}
          <div className="mockup-header flex items-center justify-between border-b border-slate-800/80 pb-2">
            <div className="flex items-center gap-2">
              <RahafitLogo size="sm" />
            </div>
            <div className="mockup-badge-live flex items-center gap-1 bg-teal-500/10 text-teal-400 text-[10px] font-extrabold px-2 py-0.5 rounded-full border border-teal-500/20">
              <Sparkles size={10} color="#14b8a6" />
              <span>LIVE DEMO</span>
            </div>
          </div>

          {/* User Greeting */}
          <div className="mockup-user-greeting">
            <div className="text-[11px] text-slate-400">
              {isRtl ? "أهلاً بك، محمد" : "Welcome back, Mohamed"}
            </div>
            <div className="text-xs font-extrabold text-amber-400">
              {isRtl ? "جاهزية اليوم: 88% (ممتازة)" : "Today's Readiness: 88% (Optimal)"}
            </div>
          </div>

          {/* Today Workout Hero Card with Ring */}
          <div className="mockup-card bg-slate-800/60 rounded-xl p-2.5 border border-slate-700/50">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <div className="mockup-icon-box bg-teal-500/20 text-teal-400 p-1.5 rounded-lg">
                  <Dumbbell size={14} />
                </div>
                <div>
                  <div className="text-[11px] font-bold text-slate-100">
                    {isRtl ? "تمرين القوة والجزء العلوي" : "Upper Body Strength"}
                  </div>
                  <div className="text-[9px] text-slate-400">
                    {isRtl ? "45 دقيقة • 4 تمارين" : "45 min • 4 exercises"}
                  </div>
                </div>
              </div>

              {/* Circular Metric Gauge (88%) */}
              <div className="mockup-ring-wrapper relative flex items-center justify-center">
                <svg width="38" height="38" viewBox="0 0 44 44">
                  <circle
                    cx="22"
                    cy="22"
                    r="18"
                    stroke="rgba(255,255,255,0.12)"
                    strokeWidth="3.5"
                    fill="none"
                  />
                  <circle
                    cx="22"
                    cy="22"
                    r="18"
                    stroke="#14b8a6"
                    strokeWidth="3.5"
                    fill="none"
                    strokeDasharray="113"
                    strokeDashoffset="13.56"
                    strokeLinecap="round"
                    transform="rotate(-90 22 22)"
                  />
                </svg>
                <span className="mockup-ring-text absolute text-[9px] font-bold text-teal-300">
                  88%
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between text-[9px] text-teal-300 pt-1 border-t border-slate-700/50">
              <span className="flex items-center gap-1">
                <CheckCircle2 size={10} />
                {isRtl ? "متكيف مع مؤشر التعافي" : "Adapted to recovery"}
              </span>
              <span className="font-bold text-amber-400">{isRtl ? "توجيه ذكي" : "Smart Plan"}</span>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="mockup-metrics-grid grid grid-cols-3 gap-1.5">
            {/* Hydration Card */}
            <div className="mockup-mini-card bg-slate-800/40 rounded-lg p-1.5 border border-slate-700/40">
              <div className="flex items-center gap-1 mb-0.5 text-cyan-400">
                <Droplets size={12} />
                <span className="text-[9px] font-bold text-slate-300">
                  {isRtl ? "الترطيب" : "Hydration"}
                </span>
              </div>
              <div className="text-xs font-extrabold text-white">2.1 L</div>
              <div className="text-[8px] text-teal-400 font-semibold">
                {isRtl ? "ممتاز" : "Good"}
              </div>
            </div>

            {/* Sleep Card */}
            <div className="mockup-mini-card bg-slate-800/40 rounded-lg p-1.5 border border-slate-700/40">
              <div className="flex items-center gap-1 mb-0.5 text-indigo-400">
                <Moon size={12} />
                <span className="text-[9px] font-bold text-slate-300">
                  {isRtl ? "النوم" : "Sleep"}
                </span>
              </div>
              <div className="text-xs font-extrabold text-white">7.8 h</div>
              <div className="text-[8px] text-teal-400 font-semibold">
                {isRtl ? "مثالي" : "Optimal"}
              </div>
            </div>

            {/* Heart Rate Card */}
            <div className="mockup-mini-card bg-slate-800/40 rounded-lg p-1.5 border border-slate-700/40">
              <div className="flex items-center gap-1 mb-0.5 text-rose-400">
                <Heart size={12} className="animate-pulse" />
                <span className="text-[9px] font-bold text-slate-300">
                  {isRtl ? "النبض" : "Heart"}
                </span>
              </div>
              <div className="text-xs font-extrabold text-white">65 bpm</div>
              <div className="text-[8px] text-slate-400">{isRtl ? "راحه" : "Rest"}</div>
            </div>
          </div>

          {/* AI Coach Quick Chat Bar */}
          <div className="mockup-ai-bar flex items-center gap-1.5 bg-slate-800/80 rounded-lg p-1.5 border border-teal-500/30">
            <Bot size={12} className="text-teal-400 shrink-0" />
            <span className="text-[9px] text-slate-300 flex-1 truncate">
              {isRtl ? "اشرح جاهزيتي اليوم مع المدرب الذكي..." : "Explain today's readiness..."}
            </span>
            <div className="mockup-send-btn bg-teal-500 text-slate-950 p-1 rounded-md">
              <Send size={8} />
            </div>
          </div>

          {/* Bottom Mockup Navigation Bar */}
          <div className="mockup-bottom-nav flex items-center justify-around pt-1 border-t border-slate-800 text-slate-400 text-[9px]">
            <div className="flex flex-col items-center gap-0.5 text-amber-400">
              <Home size={12} />
              <span>{isRtl ? "الرئيسية" : "Home"}</span>
            </div>
            <div className="flex flex-col items-center gap-0.5 hover:text-slate-200">
              <Dumbbell size={12} />
              <span>{isRtl ? "التمرين" : "Workout"}</span>
            </div>
            <div className="flex flex-col items-center gap-0.5 hover:text-slate-200">
              <Zap size={12} />
              <span>{isRtl ? "الفحص" : "Check-in"}</span>
            </div>
            <div className="flex flex-col items-center gap-0.5 hover:text-slate-200">
              <Bot size={12} />
              <span>{isRtl ? "المدرب" : "Coach"}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Cards (Decorative around phone on desktop) */}
      <HeroFloatingCard
        icon={Zap}
        title={copy.heroCardStreak}
        subtitle={isRtl ? "جاهزية 88%" : "Readiness 88%"}
        iconColor="#f59e0b"
        iconBg="rgba(245, 158, 11, 0.15)"
        className="floating-card-streak"
      />

      <HeroFloatingCard
        icon={Target}
        title={copy.heroCardGoal}
        subtitle={isRtl ? "تقدم 60%" : "60% complete"}
        iconColor="#10b981"
        iconBg="rgba(16, 185, 129, 0.15)"
        className="floating-card-goal"
      />

      <HeroFloatingCard
        icon={Bot}
        title={copy.heroCardCoach}
        subtitle={isRtl ? "توصيات متكيفة" : "Adaptive tips"}
        iconColor="#14b8a6"
        iconBg="rgba(20, 184, 166, 0.15)"
        className="floating-card-coach"
      />
    </div>
  );
};
