import { Link } from "react-router-dom";
import { ArrowRight, ArrowLeft, LogIn, Sparkles } from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Card } from "../ui";

export function FinalCtaSection() {
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  const ArrowIcon = direction === "rtl" ? ArrowLeft : ArrowRight;

  return (
    <section className="discovery-section discovery-final-cta pb-8" aria-labelledby="final-cta-title">
      <Card className="p-8 md:p-12 bg-gradient-to-r from-slate-900 via-teal-950/40 to-slate-900 border-teal-500/30 text-center flex flex-col items-center gap-4 rounded-3xl shadow-2xl relative overflow-hidden">
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage:
              "radial-gradient(circle at 50% 50%, rgba(245, 158, 11, 0.08) 0%, transparent 60%)",
          }}
          aria-hidden="true"
        />

        <h2 id="final-cta-title" className="text-2xl sm:text-4xl font-black text-white z-10">
          {copy.finalCtaHeading}
        </h2>

        <p className="text-sm sm:text-base text-slate-300 max-w-xl z-10">
          {copy.finalCtaSubheading}
        </p>

        <div className="flex flex-col sm:flex-row gap-3 pt-2 z-10 w-full sm:w-auto justify-center">
          <Link
            className="ds-button ds-button-primary bg-amber-500 hover:bg-amber-600 text-slate-950 font-extrabold px-8 py-3.5 rounded-xl shadow-lg shadow-amber-500/20 flex items-center justify-center gap-2 transition-all text-base"
            to="/register"
          >
            <Sparkles size={18} />
            <span>{copy.finalCtaPrimary}</span>
            <ArrowIcon size={18} />
          </Link>

          <Link
            className="ds-button ds-button-outline border border-slate-700 text-slate-200 hover:bg-slate-800 px-6 py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 transition-all text-base"
            to="/login"
          >
            <LogIn size={18} />
            <span>{copy.finalCtaSecondary}</span>
          </Link>
        </div>
      </Card>
    </section>
  );
}
