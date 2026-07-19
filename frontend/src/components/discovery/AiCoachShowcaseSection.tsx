import { Bot, Sparkles, Send, ShieldCheck } from "lucide-react";
import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Badge } from "../ui";

export function AiCoachShowcaseSection() {
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  const isRtl = direction === "rtl";

  return (
    <section
      id="ai-coach-showcase"
      className="ai-coach-showcase-section relative py-12 px-4 max-w-7xl mx-auto rounded-3xl bg-slate-900/40 border border-slate-800/80 overflow-hidden"
      aria-labelledby="ai-coach-showcase-title"
    >
      {/* Background Soft Radial Glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(circle at 70% 50%, rgba(139, 92, 246, 0.08) 0%, transparent 65%)",
        }}
        aria-hidden="true"
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
        {/* Left/Right Text Column */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <Badge className="inline-flex items-center gap-1.5 px-3 py-1 bg-purple-500/10 border border-purple-500/20 text-purple-400 font-extrabold text-xs tracking-wider rounded-full uppercase w-fit">
            <Sparkles size={12} className="text-amber-400" />
            <span>{copy.coachEyebrow}</span>
          </Badge>

          <h2
            id="ai-coach-showcase-title"
            className="text-2xl sm:text-3xl md:text-4xl font-black text-white tracking-tight leading-snug"
          >
            {copy.coachHeading}
          </h2>

          <p className="text-sm text-slate-300 leading-relaxed">{copy.coachSubheading}</p>

          {/* Capability Chips */}
          <div className="flex flex-wrap gap-2 pt-2">
            <span className="text-xs font-bold bg-teal-500/10 border border-teal-500/20 text-teal-300 px-3 py-1 rounded-full">
              {copy.featureAiChip1}
            </span>
            <span className="text-xs font-bold bg-amber-500/10 border border-amber-500/20 text-amber-300 px-3 py-1 rounded-full">
              {copy.featureAiChip2}
            </span>
            <span className="text-xs font-bold bg-purple-500/10 border border-purple-500/20 text-purple-300 px-3 py-1 rounded-full">
              {copy.featureAiChip3}
            </span>
            <span className="text-xs font-bold bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 px-3 py-1 rounded-full">
              {copy.featureAiChip4}
            </span>
          </div>
        </div>

        {/* Right Simulated Chat Interface Card */}
        <div className="lg:col-span-7 rounded-2xl bg-slate-950/80 border border-purple-500/20 p-5 shadow-2xl flex flex-col gap-4">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center">
                <Bot size={18} />
              </div>
              <div>
                <div className="text-xs font-bold text-white">Rahafit AI Coach</div>
                <div className="text-[10px] text-slate-400">
                  {isRtl ? "مُوجَّه بقواعد الأمان" : "Safety-bounded"}
                </div>
              </div>
            </div>
            <Badge className="bg-purple-500/10 text-purple-400 border-purple-500/20 text-[10px] font-bold">
              <ShieldCheck size={12} className="mr-1" />
              <span>SAFETY GUARD</span>
            </Badge>
          </div>

          {/* User Chat Bubble */}
          <div className="flex justify-end">
            <div className="max-w-[85%] bg-teal-600/20 border border-teal-500/30 text-teal-100 rounded-2xl rounded-tr-none px-4 py-2.5 text-xs font-medium">
              {copy.coachSamplePrompt}
            </div>
          </div>

          {/* Assistant Chat Bubble */}
          <div className="flex justify-start">
            <div className="max-w-[90%] bg-slate-900 border border-slate-800 text-slate-200 rounded-2xl rounded-tl-none px-4 py-3 text-xs leading-relaxed">
              {copy.coachSampleReply}
            </div>
          </div>

          {/* Input Bar Simulation */}
          <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-xl p-2 mt-1">
            <span className="text-xs text-slate-500 flex-1 px-2">
              {isRtl ? "اكتب سؤالك الرياضي للمدرب الذكي..." : "Ask your athletic question..."}
            </span>
            <div className="w-7 h-7 rounded-lg bg-purple-600 text-white flex items-center justify-center shrink-0">
              <Send size={12} />
            </div>
          </div>

          {/* Non-Medical Disclaimer */}
          <p className="text-[10px] text-slate-500 text-center pt-1 border-t border-slate-800/60">
            {copy.featureAiDisclaimer}
          </p>
        </div>
      </div>
    </section>
  );
}
