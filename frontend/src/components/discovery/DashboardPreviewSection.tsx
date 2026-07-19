import { Sparkles, Dumbbell, Utensils, Droplets, Bot, CheckCircle2, Zap } from "lucide-react";
import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Badge } from "../ui";

export function DashboardPreviewSection() {
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  const isRtl = direction === "rtl";

  return (
    <section
      id="dashboard-preview"
      className="dashboard-preview-section relative py-12 px-4 max-w-7xl mx-auto rounded-3xl bg-slate-900/40 border border-slate-800/80 overflow-hidden"
      aria-labelledby="dashboard-preview-title"
    >
      {/* Background Soft Glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(circle at 30% 20%, rgba(20, 184, 166, 0.08) 0%, transparent 65%)",
        }}
        aria-hidden="true"
      />

      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-10 relative z-10">
        <Badge className="inline-flex items-center gap-1.5 px-3 py-1 mb-3 bg-teal-500/10 border border-teal-500/20 text-teal-400 font-extrabold text-xs tracking-wider rounded-full uppercase">
          <Sparkles size={12} className="text-amber-400" />
          <span>{copy.previewEyebrow}</span>
        </Badge>

        <h2
          id="dashboard-preview-title"
          className="text-2xl sm:text-3xl md:text-4xl font-black text-white tracking-tight mb-3"
        >
          {copy.previewHeading}
        </h2>

        <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-normal">
          {copy.previewSubheading}
        </p>
      </div>

      {/* Illustrative Dashboard Mockup Frame */}
      <div className="relative z-10 max-w-4xl mx-auto rounded-2xl bg-slate-950/80 border border-slate-800 p-4 sm:p-6 shadow-2xl">
        {/* Mockup Header Bar */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-rose-500/80" />
            <div className="w-3 h-3 rounded-full bg-amber-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            <span className="text-xs text-slate-400 font-mono ml-2">rahafit.app/dashboard</span>
          </div>
          <Badge className="bg-teal-500/10 border border-teal-500/20 text-teal-400 text-[11px] font-bold">
            <Zap size={12} className="mr-1 text-amber-400" />
            <span>ILLUSTRATIVE PREVIEW</span>
          </Badge>
        </div>

        {/* Dashboard Grid Simulation */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          {/* Main Priority Banner (Readiness & Workout) */}
          <div className="md:col-span-8 flex flex-col gap-4">
            <div className="p-4 rounded-xl bg-gradient-to-r from-slate-900 to-teal-950/50 border border-teal-500/30 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-teal-500/20 text-teal-400 flex items-center justify-center">
                  <Dumbbell size={20} />
                </div>
                <div>
                  <div className="text-xs text-teal-400 font-extrabold">{copy.previewBadgeWorkout}</div>
                  <div className="text-sm font-bold text-white">
                    {isRtl ? "تمرين القوة والجزء العلوي (45 دقيقة)" : "Upper Body Strength (45 min)"}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-full">
                  {copy.previewBadgeReadiness}
                </span>
              </div>
            </div>

            {/* AI Insight Highlight */}
            <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start gap-3">
              <Bot size={20} className="text-teal-400 shrink-0 mt-0.5" />
              <div className="text-xs text-slate-300 leading-relaxed">
                <span className="font-bold text-white block mb-0.5">
                  {isRtl ? "توجيه المدرب الذكي:" : "AI Coach Insight:"}
                </span>
                {copy.previewInsightText}
              </div>
            </div>
          </div>

          {/* Right Metrics Sidebar */}
          <div className="md:col-span-4 flex flex-col gap-3">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <Utensils size={14} className="text-amber-400" />
                <span>{copy.previewBadgeNutrition}</span>
              </div>
              <span className="text-xs font-bold text-teal-400">2,100 kcal</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <Droplets size={14} className="text-cyan-400" />
                <span>{isRtl ? "الترطيب اليومي" : "Hydration"}</span>
              </div>
              <span className="text-xs font-bold text-cyan-400">2.1 / 3.0 L</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <CheckCircle2 size={14} className="text-emerald-400" />
                <span>{isRtl ? "الإقرار الصحي" : "Health Clearance"}</span>
              </div>
              <span className="text-xs font-bold text-emerald-400">PASS</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
