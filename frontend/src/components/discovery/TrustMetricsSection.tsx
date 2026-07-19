import { ShieldCheck, Globe, Lock, CheckCircle2 } from "lucide-react";
import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";

export function TrustMetricsSection() {
  const { locale } = useLocale();
  const copy = discoveryCopy[locale];

  const metrics = [
    {
      icon: ShieldCheck,
      title: copy.trustMetric1Title,
      desc: copy.trustMetric1Desc,
      accent: "teal",
    },
    {
      icon: Globe,
      title: copy.trustMetric2Title,
      desc: copy.trustMetric2Desc,
      accent: "amber",
    },
    {
      icon: Lock,
      title: copy.trustMetric3Title,
      desc: copy.trustMetric3Desc,
      accent: "teal",
    },
    {
      icon: CheckCircle2,
      title: copy.trustMetric4Title,
      desc: copy.trustMetric4Desc,
      accent: "amber",
    },
  ];

  return (
    <section
      id="trust-metrics"
      className="trust-metrics-section relative py-8 px-4 max-w-7xl mx-auto"
      aria-label="Product Engineering Standards"
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, idx) => {
          const Icon = metric.icon;
          const isGold = metric.accent === "amber";

          return (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800 flex items-start gap-3.5"
            >
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border ${
                  isGold
                    ? "bg-amber-500/10 border-amber-500/20 text-amber-400"
                    : "bg-teal-500/10 border-teal-500/20 text-teal-400"
                }`}
              >
                <Icon size={20} />
              </div>
              <div>
                <h3 className="text-xs font-bold text-white mb-1">{metric.title}</h3>
                <p className="text-[11px] text-slate-400 leading-relaxed">{metric.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
