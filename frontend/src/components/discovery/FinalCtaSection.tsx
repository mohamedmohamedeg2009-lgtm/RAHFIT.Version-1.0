import { Link } from "react-router-dom";
import { ArrowRight, ArrowLeft, LogIn } from "lucide-react";

import { useLocale } from "../../contexts/LocaleContext";
import { discoveryCopy } from "../../i18n/discovery";
import { Card } from "../ui";

export function FinalCtaSection() {
  const { locale, direction } = useLocale();
  const copy = discoveryCopy[locale];
  const ArrowIcon = direction === "rtl" ? ArrowLeft : ArrowRight;

  return (
    <section className="discovery-section discovery-final-cta" aria-labelledby="final-cta-title">
      <Card className="discovery-final-cta-card">
        <h2 id="final-cta-title" className="discovery-final-cta-title">
          {copy.finalCtaHeading}
        </h2>
        <p className="discovery-final-cta-subheading">{copy.finalCtaSubheading}</p>

        <div className="discovery-final-cta-actions">
          <Link className="ds-button ds-button-primary ds-button-lg" to="/register">
            <span>{copy.finalCtaPrimary}</span>
            <ArrowIcon size={18} />
          </Link>

          <Link className="ds-button ds-button-outline ds-button-lg" to="/login">
            <LogIn size={18} />
            <span>{copy.finalCtaSecondary}</span>
          </Link>
        </div>
      </Card>
    </section>
  );
}
