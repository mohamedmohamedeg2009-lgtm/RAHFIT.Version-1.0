import { LayoutDashboard, Dumbbell, Utensils, Bot, FileCheck2, CheckCircle2 } from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Card, Badge } from "../ui";

export function ProductAreasSection() {
  const { locale } = useLocale();
  const copy = discoveryCopy[locale];

  const features = [
    {
      id: "dashboard",
      icon: LayoutDashboard,
      title: copy.featureDashboardTitle,
      desc: copy.featureDashboardDesc,
      badge: copy.featureDashboardBadge,
      color: "var(--color-primary)",
    },
    {
      id: "workout",
      icon: Dumbbell,
      title: copy.featureWorkoutTitle,
      desc: copy.featureWorkoutDesc,
      badge: copy.featureWorkoutBadge,
      color: "var(--color-accent)",
    },
    {
      id: "nutrition",
      icon: Utensils,
      title: copy.featureNutritionTitle,
      desc: copy.featureNutritionDesc,
      badge: copy.featureNutritionBadge,
      color: "var(--color-success)",
    },
    {
      id: "aiCoach",
      icon: Bot,
      title: copy.featureAiCoachTitle,
      desc: copy.featureAiCoachDesc,
      badge: copy.featureAiCoachBadge,
      color: "var(--color-ai)",
    },
    {
      id: "assessment",
      icon: FileCheck2,
      title: copy.featureAssessmentTitle,
      desc: copy.featureAssessmentDesc,
      badge: copy.featureAssessmentBadge,
      color: "var(--color-warning)",
    },
  ];

  return (
    <section
      id="product-areas"
      className="discovery-section discovery-product-areas"
      aria-labelledby="product-areas-title"
    >
      <div className="discovery-section-header">
        <h2 id="product-areas-title" className="discovery-section-title">
          {copy.productAreasHeading}
        </h2>
        <p className="discovery-section-subtitle">{copy.productAreasSubheading}</p>
      </div>

      <div className="discovery-features-grid">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Card key={feature.id} className="discovery-feature-card">
              <div className="discovery-feature-header">
                <div
                  className="discovery-feature-icon-wrapper"
                  style={{
                    backgroundColor: `color-mix(in srgb, ${feature.color} 12%, transparent)`,
                  }}
                >
                  <Icon size={24} color={feature.color} />
                </div>
                <Badge className="discovery-status-badge">
                  <CheckCircle2 size={14} color="var(--color-success)" />
                  <span>{feature.badge}</span>
                </Badge>
              </div>

              <h3 className="discovery-feature-title">{feature.title}</h3>
              <p className="discovery-feature-desc">{feature.desc}</p>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
