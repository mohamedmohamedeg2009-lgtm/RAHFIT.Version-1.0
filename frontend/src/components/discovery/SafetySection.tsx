import { ShieldCheck, Activity, Stethoscope } from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Card } from "../ui";

export function SafetySection() {
  const { locale } = useLocale();
  const copy = discoveryCopy[locale];

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
      className="discovery-section discovery-safety"
      aria-labelledby="safety-section-title"
    >
      <div className="discovery-section-header">
        <h2 id="safety-section-title" className="discovery-section-title">
          {copy.safetyHeading}
        </h2>
        <p className="discovery-section-subtitle">{copy.safetySubheading}</p>
      </div>

      <div className="discovery-safety-grid">
        {safetyPoints.map((point, idx) => {
          const Icon = point.icon;
          return (
            <Card key={idx} className="discovery-safety-card">
              <div className="discovery-safety-icon-wrapper">
                <Icon size={26} color="var(--color-primary)" />
              </div>
              <div className="discovery-safety-text">
                <h3 className="discovery-safety-title">{point.title}</h3>
                <p className="discovery-safety-desc">{point.desc}</p>
              </div>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
