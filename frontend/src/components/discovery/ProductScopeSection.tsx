import { Dumbbell, Utensils, Zap, Moon, LineChart, Sparkles } from "lucide-react";
import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Badge } from "../ui";

export function ProductScopeSection() {
  const { locale } = useLocale();
  const copy = discoveryCopy[locale];

  const pillars = [
    {
      icon: Dumbbell,
      title: copy.pillar1Title,
      desc: copy.pillar1Desc,
      accent: "teal",
    },
    {
      icon: Utensils,
      title: copy.pillar2Title,
      desc: copy.pillar2Desc,
      accent: "amber",
    },
    {
      icon: Zap,
      title: copy.pillar3Title,
      desc: copy.pillar3Desc,
      accent: "teal",
    },
    {
      icon: Moon,
      title: copy.pillar4Title,
      desc: copy.pillar4Desc,
      accent: "amber",
    },
    {
      icon: LineChart,
      title: copy.pillar5Title,
      desc: copy.pillar5Desc,
      accent: "teal",
    },
  ];

  return (
    <section
      id="product-scope"
      className="product-scope-section relative py-12 px-4 max-w-7xl mx-auto rounded-3xl bg-slate-900/40 border border-slate-800/80 overflow-hidden"
      aria-labelledby="product-scope-title"
    >
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-10 relative z-10">
        <Badge className="inline-flex items-center gap-1.5 px-3 py-1 mb-3 bg-teal-500/10 border border-teal-500/20 text-teal-400 font-extrabold text-xs tracking-wider rounded-full uppercase">
          <Sparkles size={12} className="text-amber-400" />
          <span>{copy.scopeEyebrow}</span>
        </Badge>

        <h2
          id="product-scope-title"
          className="text-2xl sm:text-3xl md:text-4xl font-black text-white tracking-tight mb-3"
        >
          {copy.scopeHeading}
        </h2>

        <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-normal">
          {copy.scopeSubheading}
        </p>
      </div>

      {/* 5 Pillars Horizontal Layout */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 relative z-10">
        {pillars.map((pillar, idx) => {
          const Icon = pillar.icon;
          const isGold = pillar.accent === "amber";

          return (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800 flex flex-col gap-3 hover:border-slate-700 transition-all"
            >
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center border ${
                  isGold
                    ? "bg-amber-500/10 border-amber-500/20 text-amber-400"
                    : "bg-teal-500/10 border-teal-500/20 text-teal-400"
                }`}
              >
                <Icon size={20} />
              </div>
              <h3 className="text-base font-bold text-white">{pillar.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{pillar.desc}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
