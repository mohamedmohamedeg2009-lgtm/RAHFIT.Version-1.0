import { Link } from "react-router-dom";
import { Check, Sparkles } from "lucide-react";
import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Card, Badge } from "../ui";

export function PricingSection() {
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  const isRtl = direction === "rtl";

  return (
    <section
      id="pricing"
      className="pricing-section py-12 px-4 max-w-7xl mx-auto"
      aria-labelledby="pricing-title"
    >
      <div className="text-center mb-8">
        <Badge className="inline-flex items-center gap-1.5 px-3 py-1 mb-3 bg-amber-500/10 border border-amber-500/20 text-amber-400 font-extrabold text-xs tracking-wider rounded-full uppercase">
          <Sparkles size={12} className="text-amber-400" />
          <span>{isRtl ? "الباقة الحالية" : "CURRENT ACCESS TIER"}</span>
        </Badge>
        <h2 id="pricing-title" className="text-2xl sm:text-3xl font-extrabold text-white mb-2">
          {copy.pricingHeading}
        </h2>
        <p className="text-slate-400 text-sm max-w-2xl mx-auto">{copy.pricingSubheading}</p>
      </div>

      <Card className="max-w-md mx-auto p-8 bg-slate-900/60 border-amber-500/30 text-center flex flex-col gap-6 shadow-xl relative overflow-hidden">
        <div className="flex flex-col items-center gap-2">
          <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20 px-3 py-1 font-bold text-xs rounded-full">
            {copy.pricingFreeTitle}
          </Badge>
          <div className="text-3xl sm:text-4xl font-black text-white pt-2">
            {isRtl ? "مجاني بالكامل" : "100% Free"}
          </div>
          <p className="text-xs text-slate-300 max-w-xs">{copy.pricingFreeDesc}</p>
        </div>

        {/* Included Features Checklist */}
        <div className="flex flex-col gap-2.5 text-left border-t border-b border-slate-800 py-4 text-xs font-semibold text-slate-200">
          <div className="flex items-center gap-2">
            <Check size={14} className="text-amber-400 shrink-0" />
            <span>{isRtl ? "التقييم الذكي والإقرار الصحي" : "Smart Assessment & Clearance"}</span>
          </div>
          <div className="flex items-center gap-2">
            <Check size={14} className="text-amber-400 shrink-0" />
            <span>{isRtl ? "توليد وتنفيذ التمارين الذكية" : "Intelligent Workout Generation"}</span>
          </div>
          <div className="flex items-center gap-2">
            <Check size={14} className="text-amber-400 shrink-0" />
            <span>{isRtl ? "سجل التغذية واستهلاك الماء" : "Nutrition & Water Tracking"}</span>
          </div>
          <div className="flex items-center gap-2">
            <Check size={14} className="text-amber-400 shrink-0" />
            <span>{isRtl ? "فحص الجاهزية واستشارات المدرب" : "Daily Readiness & AI Coach"}</span>
          </div>
        </div>

        <Link
          to="/register"
          className="ds-button ds-button-primary bg-amber-500 hover:bg-amber-600 text-slate-950 font-extrabold py-3.5 rounded-xl shadow-lg shadow-amber-500/20 transition-all text-sm"
        >
          {copy.landingHeroPrimaryCta}
        </Link>
      </Card>
    </section>
  );
}
