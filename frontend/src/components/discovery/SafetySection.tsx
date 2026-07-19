import { ShieldCheck, Activity, Stethoscope, CheckCircle2, AlertTriangle } from "lucide-react";
import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Badge } from "../ui";

export function SafetySection() {
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  const isRtl = direction === "rtl";

  const safetyPoints = [
    {
      icon: Activity,
      title: copy.safetyPoint1Title,
      desc: copy.safetyPoint1Desc,
    },
    {
      icon: ShieldCheck,
      title: copy.safetyPoint2Title,
      desc: copy.safetyPoint2Desc,
    },
    {
      icon: Stethoscope,
      title: copy.safetyPoint3Title,
      desc: copy.safetyPoint3Desc,
    },
  ];

  return (
    <section
      id="safety-section"
      className="safety-section relative py-12 px-4 max-w-7xl mx-auto rounded-3xl bg-slate-900/40 border border-teal-500/20 overflow-hidden"
      aria-labelledby="safety-section-title"
    >
      {/* Background Glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(circle at 20% 50%, rgba(20, 184, 166, 0.08) 0%, transparent 65%)",
        }}
        aria-hidden="true"
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
        {/* Left Column: Copy & Safety Principles */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          <div className="flex items-center gap-3 text-teal-400">
            <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center">
              <ShieldCheck size={24} />
            </div>
            <div>
              <h2 id="safety-section-title" className="text-2xl sm:text-3xl font-extrabold text-white">
                {copy.safetyHeading}
              </h2>
            </div>
          </div>

          <p className="text-sm text-slate-300 leading-relaxed">
            {copy.safetySubheading}
          </p>

          <div className="flex flex-col gap-4">
            {safetyPoints.map((point, idx) => {
              const Icon = point.icon;
              return (
                <div key={idx} className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
                  <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center shrink-0 mt-0.5">
                    <Icon size={18} />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white mb-0.5">{point.title}</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">{point.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Illustrative Safety Shield & Guard Card */}
        <div className="lg:col-span-5 rounded-2xl bg-slate-950/90 border border-teal-500/30 p-6 shadow-2xl flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <ShieldCheck size={20} className="text-teal-400" />
              <span className="text-xs font-bold text-white">
                {isRtl ? "درع الأمان والخصوصية" : "Safety Guard Active"}
              </span>
            </div>
            <Badge className="bg-teal-500/10 text-teal-400 border-teal-500/20 text-[10px] font-bold">
              ENFORCED
            </Badge>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col gap-3">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
              <span>{isRtl ? "الإقرار الصحي" : "Medical Declaration"}</span>
              <span className="text-emerald-400 flex items-center gap-1 font-bold">
                <CheckCircle2 size={12} />
                {isRtl ? "مكتمل" : "Verified"}
              </span>
            </div>

            <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
              <span>{isRtl ? "متابعة الألم" : "Pain Flag Boundaries"}</span>
              <span className="text-teal-400 font-bold">{isRtl ? "تنبيه تلقائي" : "Active Check"}</span>
            </div>

            <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
              <span>{isRtl ? "سرية البيانات" : "Data Scope"}</span>
              <span className="text-amber-400 font-bold">{isRtl ? "حساب شخصي مشفر" : "Owner Scoped"}</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-start gap-2.5 text-xs text-teal-300">
            <AlertTriangle size={16} className="text-amber-400 shrink-0 mt-0.5" />
            <span>
              {isRtl
                ? "عند الإبلاغ عن ألم، يوقف النظام التمارين المتأثرة فوراً ويقترح بدائل آمنة أو أيام راحة."
                : "When pain is reported, affected exercises are automatically substituted or rest days assigned."}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
