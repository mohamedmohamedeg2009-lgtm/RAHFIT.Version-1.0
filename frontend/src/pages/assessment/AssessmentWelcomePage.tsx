import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

import { BrandLogo } from "../../components/common/BrandLogo";
import { Button, Card, FullPageLoader } from "../../components/ui";
import { useAssessment } from "../../contexts/AssessmentContext";
import { useLocale } from "../../contexts/LocaleContext";
import { assessmentCopy } from "../../i18n/assessment";

export default function AssessmentWelcomePage() {
  const { locale } = useLocale();
  const copy = assessmentCopy[locale];
  const { session, start, isLoading, error, clearError } = useAssessment();
  const navigate = useNavigate();
  const checked = useRef(false);

  useEffect(() => {
    if (checked.current) return;
    checked.current = true;
    void start()
      .then((loaded) => {
        if (loaded.answers.length > 0) {
          navigate(`/assessment/resume/${loaded.id}`, { replace: true });
        }
      })
      .catch(() => undefined);
  }, [navigate, start]);

  const begin = async () => {
    clearError();
    try {
      const active = session ?? (await start());
      navigate(`/assessment/session/${active.id}`);
    } catch {
      // The context exposes the safe API error in the page.
    }
  };

  if (isLoading && !session && !error) return <FullPageLoader label={copy.starting} />;

  return (
    <main className="assessment-main assessment-welcome-main">
      <section className="assessment-welcome" aria-labelledby="assessment-welcome-title">
        <div className="assessment-welcome-copy">
          <span className="assessment-eyebrow">{copy.welcomeEyebrow}</span>
          <h1 id="assessment-welcome-title">{copy.welcomeTitle}</h1>
          <p>{copy.welcomeBody}</p>
          {error ? (
            <div className="assessment-inline-error" role="alert">
              <span>{error.message || copy.loadError}</span>
              <Button variant="ghost" size="sm" onClick={() => void begin()}>
                {copy.retry}
              </Button>
            </div>
          ) : null}
          <div className="assessment-welcome-actions">
            <Button size="lg" onClick={() => void begin()} loading={isLoading}>
              {copy.start}
              <span aria-hidden="true">→</span>
            </Button>
            <small>{copy.privacy}</small>
          </div>
        </div>
        <div className="assessment-orbit" aria-hidden="true">
          <BrandLogo className="assessment-orbit-wordmark" />
          <span className="assessment-orbit-ring ring-one" />
          <span className="assessment-orbit-ring ring-two" />
          <span className="assessment-orbit-dot dot-one" />
          <span className="assessment-orbit-dot dot-two" />
          <span className="assessment-orbit-dot dot-three" />
        </div>
      </section>
      <section className="assessment-benefits" aria-label={copy.assessment}>
        {[
          [copy.adaptive, copy.adaptiveBody, "01"],
          [copy.safe, copy.safeBody, "02"],
          [copy.resumable, copy.resumableBody, "03"],
        ].map(([title, body, number]) => (
          <Card key={title} className="assessment-benefit-card">
            <span>{number}</span>
            <h2>{title}</h2>
            <p>{body}</p>
          </Card>
        ))}
      </section>
    </main>
  );
}
