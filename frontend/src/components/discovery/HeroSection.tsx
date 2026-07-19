import { Link } from "react-router-dom";
import { Sparkles, ArrowRight, ArrowLeft, ShieldCheck, ChevronDown } from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Badge } from "../ui";

export function HeroSection() {
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  const ArrowIcon = direction === "rtl" ? ArrowLeft : ArrowRight;

  return (
    <section className="discovery-hero" aria-labelledby="discovery-hero-title">
      <div className="discovery-hero-content">
        <Badge className="discovery-trust-badge">
          <ShieldCheck size={16} />
          <span>{copy.heroTrustBadge}</span>
        </Badge>

        <h1 id="discovery-hero-title" className="discovery-hero-title">
          {copy.heroHeading}
        </h1>

        <p className="discovery-hero-subtitle">{copy.heroSubheading}</p>

        <div className="discovery-hero-actions">
          <Link className="ds-button ds-button-primary ds-button-lg" to="/register">
            <span>{copy.heroPrimaryCta}</span>
            <ArrowIcon size={18} />
          </Link>

          <a href="#product-areas" className="ds-button ds-button-outline ds-button-lg">
            <span>{copy.heroSecondaryCta}</span>
            <ChevronDown size={18} />
          </a>
        </div>

        <div className="discovery-hero-skip">
          <Link to="/register" className="discovery-skip-link">
            <span>{copy.heroSkipLink}</span>
            <Sparkles size={14} />
          </Link>
        </div>
      </div>
    </section>
  );
}
