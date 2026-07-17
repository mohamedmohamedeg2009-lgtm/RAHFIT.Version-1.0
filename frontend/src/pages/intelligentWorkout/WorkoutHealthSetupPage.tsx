import {
  useEffect,
  useRef,
  useState,
  type Dispatch,
  type FormEvent,
  type SetStateAction,
} from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import {
  Alert,
  Button,
  Card,
  Checkbox,
  Input,
  Select,
  Skeleton,
  Textarea,
} from "../../components/ui";
import { ApiError } from "../../services/apiClient";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { HealthProfileRequest, HealthSeverity } from "../../types/intelligentWorkout";
import { useLocale } from "../../contexts/LocaleContext";
import { workoutEnumLabel, workoutText } from "../../i18n/intelligentWorkout";

const empty: HealthProfileRequest = {
  injuries: [],
  chronic_conditions: [],
  pain_areas: [],
  mobility_limitations: [],
  surgery_history: [],
};
export default function WorkoutHealthSetupPage() {
  const { locale } = useLocale();
  const t = (key: Parameters<typeof workoutText>[1]) => workoutText(locale, key);
  const severityOptions = ["mild", "moderate", "severe"].map((value) => ({
    value,
    label: workoutEnumLabel(value, locale),
  }));
  const navigate = useNavigate();
  const location = useLocation();
  const dirty = useRef(false);
  const profileSaved = Boolean((location.state as { profileSaved?: boolean } | null)?.profileSaved);
  const [data, setDataState] = useState<HealthProfileRequest>(empty);
  const [loading, setLoading] = useState(true);
  const [hasExisting, setHasExisting] = useState<boolean | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const setData: Dispatch<SetStateAction<HealthProfileRequest>> = (action) => {
    dirty.current = true;
    setDataState(action);
  };
  useEffect(() => {
    let active = true;
    void intelligentWorkoutService
      .getHealthProfile()
      .then((profile) => {
        if (!active) return;
        setHasExisting(true);
        if (!dirty.current) setDataState(profile);
      })
      .catch((cause: unknown) => {
        if (!active) return;
        if (cause instanceof ApiError && cause.status === 404) setHasExisting(false);
        else setError(mapWorkoutError(cause, locale));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [locale]);
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!confirmed) return;
    setSaving(true);
    setError(null);
    try {
      await intelligentWorkoutService.updateHealthProfile(data);
      await intelligentWorkoutService.getHealthProfile();
      navigate("/intelligent-workouts/generate", { state: { healthSaved: true } });
    } catch (cause) {
      setError(mapWorkoutError(cause, locale));
    } finally {
      setSaving(false);
    }
  };
  return (
    <IntelligentWorkoutShell title={t("healthTitle")} description={t("healthDescription")}>
      {profileSaved ? (
        <Alert variant="success" title={t("profileSaved")}>
          <p>{t("profileSavedDescription")}</p>
        </Alert>
      ) : null}
      <Alert variant="warning" title={t("healthPrivacy")}>
        <p>{t("healthPrivacyDescription")}</p>
      </Alert>
      {error ? <WorkoutErrorAlert error={error} /> : null}
      {loading ? (
        <Card aria-live="polite" aria-busy="true">
          <span className="sr-only">{t("loadingSavedHealth")}</span>
          <Skeleton height="12rem" />
        </Card>
      ) : (
        <>
          {hasExisting === false ? (
            <Alert variant="info" title={t("noSavedHealth")}>
              <p>{t("noSavedHealthDescription")}</p>
            </Alert>
          ) : hasExisting ? (
            <Alert variant="success" title={t("savedHealthLoaded")}>
              <p>{t("savedHealthLoadedDescription")}</p>
            </Alert>
          ) : null}
          <form className="iw-setup-form" onSubmit={(event) => void submit(event)}>
            <HealthGroup
              title={t("injuries")}
              emptyLabel={t("noInjuries")}
              addLabel={workoutText(locale, "addItem", { item: t("injuries") })}
              onAdd={() =>
                setData((value) => ({
                  ...value,
                  injuries: [
                    ...value.injuries,
                    {
                      area: "",
                      description: "",
                      severity: "mild",
                      active: true,
                      medically_cleared: false,
                    },
                  ],
                }))
              }
              count={data.injuries.length}
            >
              {data.injuries.map((item, index) => (
                <RecordCard
                  key={index}
                  title={workoutText(locale, "injuryNumber", { count: index + 1 })}
                  onRemove={() =>
                    setData((value) => ({
                      ...value,
                      injuries: value.injuries.filter((_, itemIndex) => itemIndex !== index),
                    }))
                  }
                >
                  <Input
                    label={t("area")}
                    required
                    value={item.area}
                    onChange={(event) =>
                      edit("injuries", index, { ...item, area: event.target.value })
                    }
                  />
                  <Textarea
                    label={t("description")}
                    required
                    maxLength={300}
                    value={item.description}
                    onChange={(event) =>
                      edit("injuries", index, { ...item, description: event.target.value })
                    }
                  />
                  <Select
                    label={t("severity")}
                    value={item.severity}
                    options={severityOptions}
                    onChange={(event) =>
                      edit("injuries", index, {
                        ...item,
                        severity: event.target.value as HealthSeverity,
                      })
                    }
                  />
                  <Checkbox
                    label={t("currentlyActive")}
                    checked={item.active}
                    onChange={(event) =>
                      edit("injuries", index, { ...item, active: event.target.checked })
                    }
                  />
                  <Checkbox
                    label={t("medicallyCleared")}
                    checked={item.medically_cleared}
                    onChange={(event) =>
                      edit("injuries", index, { ...item, medically_cleared: event.target.checked })
                    }
                  />
                </RecordCard>
              ))}
            </HealthGroup>
            <HealthGroup
              title={t("chronicConditions")}
              emptyLabel={t("noConditions")}
              addLabel={workoutText(locale, "addItem", { item: t("chronicConditions") })}
              onAdd={() =>
                setData((value) => ({
                  ...value,
                  chronic_conditions: [
                    ...value.chronic_conditions,
                    { name: "", controlled: false, medically_cleared: false },
                  ],
                }))
              }
              count={data.chronic_conditions.length}
            >
              {data.chronic_conditions.map((item, index) => (
                <RecordCard
                  key={index}
                  title={workoutText(locale, "conditionNumber", { count: index + 1 })}
                  onRemove={() =>
                    setData((value) => ({
                      ...value,
                      chronic_conditions: value.chronic_conditions.filter(
                        (_, itemIndex) => itemIndex !== index,
                      ),
                    }))
                  }
                >
                  <Input
                    label={t("conditionName")}
                    required
                    value={item.name}
                    onChange={(event) =>
                      edit("chronic_conditions", index, { ...item, name: event.target.value })
                    }
                  />
                  <Checkbox
                    label={t("conditionControlled")}
                    checked={item.controlled}
                    onChange={(event) =>
                      edit("chronic_conditions", index, {
                        ...item,
                        controlled: event.target.checked,
                      })
                    }
                  />
                  <Checkbox
                    label={t("medicallyCleared")}
                    checked={item.medically_cleared}
                    onChange={(event) =>
                      edit("chronic_conditions", index, {
                        ...item,
                        medically_cleared: event.target.checked,
                      })
                    }
                  />
                </RecordCard>
              ))}
            </HealthGroup>
            <HealthGroup
              title={t("painAreas")}
              emptyLabel={t("noPainAreas")}
              addLabel={workoutText(locale, "addItem", { item: t("painAreas") })}
              onAdd={() =>
                setData((value) => ({
                  ...value,
                  pain_areas: [
                    ...value.pain_areas,
                    { area: "", intensity: 1, movement_related: false },
                  ],
                }))
              }
              count={data.pain_areas.length}
            >
              {data.pain_areas.map((item, index) => (
                <RecordCard
                  key={index}
                  title={workoutText(locale, "painAreaNumber", { count: index + 1 })}
                  onRemove={() =>
                    setData((value) => ({
                      ...value,
                      pain_areas: value.pain_areas.filter((_, itemIndex) => itemIndex !== index),
                    }))
                  }
                >
                  <Input
                    label={t("area")}
                    required
                    value={item.area}
                    onChange={(event) =>
                      edit("pain_areas", index, { ...item, area: event.target.value })
                    }
                  />
                  <Input
                    label={t("intensity")}
                    type="number"
                    min={0}
                    max={10}
                    value={item.intensity}
                    onChange={(event) =>
                      edit("pain_areas", index, { ...item, intensity: Number(event.target.value) })
                    }
                  />
                  <Checkbox
                    label={t("movementRelated")}
                    checked={item.movement_related}
                    onChange={(event) =>
                      edit("pain_areas", index, { ...item, movement_related: event.target.checked })
                    }
                  />
                </RecordCard>
              ))}
            </HealthGroup>
            <HealthGroup
              title={t("mobilityLimitations")}
              emptyLabel={t("noLimitations")}
              addLabel={workoutText(locale, "addItem", { item: t("mobilityLimitations") })}
              onAdd={() =>
                setData((value) => ({
                  ...value,
                  mobility_limitations: [
                    ...value.mobility_limitations,
                    { area: "", description: "", severity: "mild" },
                  ],
                }))
              }
              count={data.mobility_limitations.length}
            >
              {data.mobility_limitations.map((item, index) => (
                <RecordCard
                  key={index}
                  title={workoutText(locale, "limitationNumber", { count: index + 1 })}
                  onRemove={() =>
                    setData((value) => ({
                      ...value,
                      mobility_limitations: value.mobility_limitations.filter(
                        (_, itemIndex) => itemIndex !== index,
                      ),
                    }))
                  }
                >
                  <Input
                    label={t("area")}
                    required
                    value={item.area}
                    onChange={(event) =>
                      edit("mobility_limitations", index, { ...item, area: event.target.value })
                    }
                  />
                  <Textarea
                    label={t("description")}
                    required
                    maxLength={300}
                    value={item.description}
                    onChange={(event) =>
                      edit("mobility_limitations", index, {
                        ...item,
                        description: event.target.value,
                      })
                    }
                  />
                  <Select
                    label={t("severity")}
                    value={item.severity}
                    options={severityOptions}
                    onChange={(event) =>
                      edit("mobility_limitations", index, {
                        ...item,
                        severity: event.target.value as HealthSeverity,
                      })
                    }
                  />
                </RecordCard>
              ))}
            </HealthGroup>
            <HealthGroup
              title={t("surgeryHistory")}
              emptyLabel={t("noSurgeries")}
              addLabel={workoutText(locale, "addItem", { item: t("surgeryHistory") })}
              onAdd={() =>
                setData((value) => ({
                  ...value,
                  surgery_history: [
                    ...value.surgery_history,
                    { procedure: "", surgery_date: "", medically_cleared: false },
                  ],
                }))
              }
              count={data.surgery_history.length}
            >
              {data.surgery_history.map((item, index) => (
                <RecordCard
                  key={index}
                  title={workoutText(locale, "surgeryNumber", { count: index + 1 })}
                  onRemove={() =>
                    setData((value) => ({
                      ...value,
                      surgery_history: value.surgery_history.filter(
                        (_, itemIndex) => itemIndex !== index,
                      ),
                    }))
                  }
                >
                  <Input
                    label={t("procedure")}
                    required
                    value={item.procedure}
                    onChange={(event) =>
                      edit("surgery_history", index, { ...item, procedure: event.target.value })
                    }
                  />
                  <Input
                    label={t("surgeryDate")}
                    type="date"
                    required
                    max={new Date().toISOString().slice(0, 10)}
                    value={item.surgery_date}
                    onChange={(event) =>
                      edit("surgery_history", index, { ...item, surgery_date: event.target.value })
                    }
                  />
                  <Checkbox
                    label={t("medicallyCleared")}
                    checked={item.medically_cleared}
                    onChange={(event) =>
                      edit("surgery_history", index, {
                        ...item,
                        medically_cleared: event.target.checked,
                      })
                    }
                  />
                </RecordCard>
              ))}
            </HealthGroup>
            <Card>
              <Checkbox
                label={t("confirmHealth")}
                description={t("confirmHealthDescription")}
                checked={confirmed}
                onChange={(event) => setConfirmed(event.target.checked)}
              />
            </Card>
            <div className="iw-form-footer">
              <Button size="lg" type="submit" disabled={!confirmed} loading={saving}>
                {t("saveHealth")}
              </Button>
            </div>
          </form>
        </>
      )}
    </IntelligentWorkoutShell>
  );

  function edit<K extends keyof HealthProfileRequest>(
    key: K,
    index: number,
    value: HealthProfileRequest[K][number],
  ) {
    setData((current) => ({
      ...current,
      [key]: current[key].map((item, itemIndex) => (itemIndex === index ? value : item)),
    }));
  }
}

function HealthGroup({
  title,
  emptyLabel,
  addLabel,
  count,
  onAdd,
  children,
}: {
  title: string;
  emptyLabel: string;
  addLabel: string;
  count: number;
  onAdd: () => void;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <fieldset>
        <legend>{title}</legend>
        {count ? (
          <div className="iw-record-list">{children}</div>
        ) : (
          <p className="muted-text">{emptyLabel}</p>
        )}
        <Button type="button" variant="outline" onClick={onAdd}>
          {addLabel}
        </Button>
      </fieldset>
    </Card>
  );
}

function RecordCard({
  title,
  onRemove,
  children,
}: {
  title: string;
  onRemove: () => void;
  children: React.ReactNode;
}) {
  const { locale } = useLocale();
  return (
    <section className="iw-record">
      <div className="iw-record-heading">
        <h3>{title}</h3>
        <Button type="button" variant="ghost" size="sm" onClick={onRemove}>
          {workoutText(locale, "remove")}
        </Button>
      </div>
      <div className="iw-form-grid">{children}</div>
    </section>
  );
}
