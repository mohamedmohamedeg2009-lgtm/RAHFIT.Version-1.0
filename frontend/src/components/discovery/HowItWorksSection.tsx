import { UserPlus, ClipboardList, Shield, LayoutDashboard } from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Card } from "../ui";

export function HowItWorksSection() {
  const { locale } = useLocale();
  const copy = discoveryCopy[locale];

  const steps = [
    {
      number: "01",
      icon: UserPlus,
      title: copy.step1Title,
      desc: copy.step1Desc,
    },
    {
      number: "02",
      icon: ClipboardList,
      title: copy.step2Title,
      desc: copy.step2Desc,
    },
    {
      number: "03",
      icon: Shield,
      title: copy.step3Title,
      desc: copy.step3Desc,
    },
    {
      number: "04",
      icon: LayoutDashboard,
      title: copy.step4Title,
      desc: copy.step4Desc,
    },
  ];

  return (
    <section
      id="how-it-works"
      className="discovery-section discovery-how-it-works"
      aria-labelledby="how-it-works-title"
    >
      <div className="discovery-section-header">
        <h2 id="how-it-works-title" className="discovery-section-title">
          {copy.howItWorksHeading}
        </h2>
        <p className="discovery-section-subtitle">{copy.howItWorksSubheading}</p>
      </div>

      <div className="discovery-steps-grid">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <Card key={step.number} className="discovery-step-card">
              <div className="discovery-step-header">
                <span className="discovery-step-number">{step.number}</span>
                <div className="discovery-step-icon-wrapper">
                  <Icon size={24} color="var(--color-primary)" />
                </div>
              </div>
              <h3 className="discovery-step-title">{step.title}</h3>
              <p className="discovery-step-desc">{step.desc}</p>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
