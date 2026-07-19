import React from "react";
import {
  Dumbbell,
  Flame,
  Droplets,
  Moon,
  Heart,
  Bot,
  Send,
  Target,
  Sparkles,
  CheckCircle2,
} from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { HeroFloatingCard } from "./HeroFloatingCard";

export const HeroPhoneMockup: React.FC = () => {
  const { locale } = useLocale();
  const copy = discoveryCopy[locale];
  const isRtl = locale === "ar";

  return (
    <div className="hero-mockup-wrapper" aria-label="Rahfit App Demo Interface">
      {/* Smartphone frame container */}
      <div className="hero-phone-frame">
        {/* Dynamic Island / Notch */}
        <div className="hero-phone-notch">
          <div className="hero-phone-camera" />
          <div className="hero-phone-speaker" />
        </div>

        {/* Screen inner UI */}
        <div className="hero-phone-screen" dir={isRtl ? "rtl" : "ltr"}>
          {/* Header Bar */}
          <div className="mockup-header">
            <div className="mockup-user flex items-center gap-2">
              <div className="mockup-avatar">R</div>
              <div>
                <div className="mockup-user-name">
                  {isRtl ? "أهلاً بك، محمد" : "Welcome back, Mohamed"}
                </div>
                <div className="mockup-user-sub font-medium">
                  {isRtl ? "لوحة التحكم اليومية" : "Today's Command Center"}
                </div>
              </div>
            </div>
            <div className="mockup-badge-live">
              <Sparkles size={12} color="#14b8a6" />
              <span>LIVE</span>
            </div>
          </div>

          {/* Today Workout Hero Card */}
          <div className="mockup-card mockup-workout-card">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="mockup-icon-box bg-teal-500/20 text-teal-400">
                  <Dumbbell size={16} />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-100">
                    {isRtl ? "تمرين القوة والجزء العلوي" : "Upper Body Strength"}
                  </div>
                  <div className="text-[10px] text-slate-400">
                    {isRtl ? "45 دقيقة • 4 تمارين" : "45 min • 4 exercises"}
                  </div>
                </div>
              </div>

              {/* Circular Metric Gauge (64%) */}
              <div className="mockup-ring-wrapper">
                <svg width="44" height="44" viewBox="0 0 44 44">
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
                    strokeDashoffset="40.68"
                    strokeLinecap="round"
                    transform="rotate(-90 22 22)"
                  />
                </svg>
                <span className="mockup-ring-text">64%</span>
              </div>
            </div>

            <div className="flex items-center justify-between text-[11px] text-teal-300 pt-1 border-t border-slate-700/50">
              <span className="flex items-center gap-1">
                <CheckCircle2 size={12} />
                {isRtl ? "البرنامج متكيف مع الجاهزية" : "Adapted to readiness"}
              </span>
              <span className="font-bold">{isRtl ? "مستمر الان" : "In Progress"}</span>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="mockup-metrics-grid">
            {/* Water Card */}
            <div className="mockup-mini-card">
              <div className="flex items-center gap-1.5 mb-1 text-cyan-400">
                <Droplets size={14} />
                <span className="text-[10px] font-bold text-slate-300">
                  {isRtl ? "الترطيب" : "Hydration"}
                </span>
              </div>
              <div className="text-sm font-extrabold text-white">1.9 L</div>
              <div className="text-[9px] text-slate-400">{isRtl ? "من 2.5 L" : "of 2.5 L"}</div>
            </div>

            {/* Sleep Card */}
            <div className="mockup-mini-card">
              <div className="flex items-center gap-1.5 mb-1 text-indigo-400">
                <Moon size={14} />
                <span className="text-[10px] font-bold text-slate-300">
                  {isRtl ? "النوم والتعافي" : "Sleep & Rest"}
                </span>
              </div>
              <div className="text-sm font-extrabold text-white">7.5 h</div>
              <div className="text-[9px] text-teal-400 font-semibold">
                {isRtl ? "جيد جداً" : "Optimal"}
              </div>
            </div>

            {/* Heart Rate Card */}
            <div className="mockup-mini-card">
              <div className="flex items-center gap-1.5 mb-1 text-rose-400">
                <Heart size={14} className="animate-pulse" />
                <span className="text-[10px] font-bold text-slate-300">
                  {isRtl ? "نبض النبض" : "Heart Rate"}
                </span>
              </div>
              <div className="text-sm font-extrabold text-white">68 bpm</div>
              <div className="text-[9px] text-slate-400">{isRtl ? "راحة هادئة" : "Resting"}</div>
            </div>
          </div>

          {/* Weekly Progress Bar Chart */}
          <div className="mockup-card mockup-chart-card">
            <div className="flex justify-between items-center mb-2">
              <span className="text-[11px] font-bold text-slate-200">
                {isRtl ? "الالتزام الأسبوعي" : "Weekly Activity"}
              </span>
              <span className="text-[10px] text-teal-400 font-bold">92%</span>
            </div>
            <div className="mockup-bars flex items-end justify-between h-10 gap-1.5 pt-1">
              {[65, 80, 45, 90, 85, 100, 75].map((val, idx) => (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                  <div
                    className={`w-full rounded-t-sm ${
                      idx === 5
                        ? "bg-teal-400 shadow-[0_0_8px_rgba(20,184,166,0.6)]"
                        : "bg-slate-700"
                    }`}
                    style={{ height: `${val}%` }}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* AI Coach Chat Preview Bar */}
          <div className="mockup-ai-bar">
            <Bot size={14} className="text-teal-400 shrink-0" />
            <span className="text-[10px] text-slate-400 flex-1 truncate">
              {isRtl ? "اسأل المدرب الذكي عن البدائل..." : "Ask AI Coach for advice..."}
            </span>
            <div className="mockup-send-btn">
              <Send size={10} color="#ffffff" />
            </div>
          </div>
        </div>
      </div>

      {/* Floating Cards (Decorative around the phone on desktop) */}
      <HeroFloatingCard
        icon={Flame}
        title={copy.heroCardStreak}
        subtitle={isRtl ? "استمراريةممتازة" : "Great consistency"}
        iconColor="#f97316"
        iconBg="rgba(249, 115, 22, 0.15)"
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

      <HeroFloatingCard
        icon={Dumbbell}
        title={copy.heroCardWorkout}
        subtitle={isRtl ? "الخطة الذكية" : "Smart plan"}
        iconColor="#06b6d4"
        iconBg="rgba(6, 182, 212, 0.15)"
        className="floating-card-workout"
      />
    </div>
  );
};
