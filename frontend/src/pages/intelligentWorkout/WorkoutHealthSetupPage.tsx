import { useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { Alert, Button, Card, Checkbox, Input, Select, Textarea } from "../../components/ui";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { HealthProfileRequest, HealthSeverity } from "../../types/intelligentWorkout";

const empty: HealthProfileRequest = {
  injuries: [],
  chronic_conditions: [],
  pain_areas: [],
  mobility_limitations: [],
  surgery_history: [],
};
const severityOptions = ["mild", "moderate", "severe"].map((value) => ({
  value,
  label: value[0].toUpperCase() + value.slice(1),
}));

export default function WorkoutHealthSetupPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const profileSaved = Boolean((location.state as { profileSaved?: boolean } | null)?.profileSaved);
  const [data, setData] = useState<HealthProfileRequest>(empty);
  const [confirmed, setConfirmed] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!confirmed) return;
    setSaving(true);
    setError(null);
    try {
      await intelligentWorkoutService.updateHealthProfile(data);
      navigate("/intelligent-workouts/generate", { state: { healthSaved: true } });
    } catch (cause) {
      setError(mapWorkoutError(cause));
    } finally {
      setSaving(false);
    }
  };
  return (
    <IntelligentWorkoutShell
      title="Health declaration"
      description="Declare relevant health information so server safety rules can decide whether training is appropriate."
    >
      {profileSaved ? (
        <Alert variant="success" title="Profile saved">
          <p>Your training profile is ready. Complete this declaration to continue.</p>
        </Alert>
      ) : null}
      <Alert variant="warning" title="Health and privacy">
        <p>
          This information is used for training safety. It is not a diagnosis and does not replace a
          qualified clinician. Seek professional care for serious or unusual symptoms. Do not enter
          private free-text notes.
        </p>
      </Alert>
      {error ? <WorkoutErrorAlert error={error} /> : null}
      <form className="iw-setup-form" onSubmit={(event) => void submit(event)}>
        <HealthGroup
          title="Injuries"
          emptyLabel="No injuries declared"
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
              title={`Injury ${index + 1}`}
              onRemove={() =>
                setData((value) => ({
                  ...value,
                  injuries: value.injuries.filter((_, itemIndex) => itemIndex !== index),
                }))
              }
            >
              <Input
                label="Area"
                required
                value={item.area}
                onChange={(event) => edit("injuries", index, { ...item, area: event.target.value })}
              />
              <Textarea
                label="Description"
                required
                maxLength={300}
                value={item.description}
                onChange={(event) =>
                  edit("injuries", index, { ...item, description: event.target.value })
                }
              />
              <Select
                label="Severity"
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
                label="Currently active"
                checked={item.active}
                onChange={(event) =>
                  edit("injuries", index, { ...item, active: event.target.checked })
                }
              />
              <Checkbox
                label="Medically cleared"
                checked={item.medically_cleared}
                onChange={(event) =>
                  edit("injuries", index, { ...item, medically_cleared: event.target.checked })
                }
              />
            </RecordCard>
          ))}
        </HealthGroup>
        <HealthGroup
          title="Chronic conditions"
          emptyLabel="No chronic conditions declared"
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
              title={`Condition ${index + 1}`}
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
                label="Condition name"
                required
                value={item.name}
                onChange={(event) =>
                  edit("chronic_conditions", index, { ...item, name: event.target.value })
                }
              />
              <Checkbox
                label="Condition is controlled"
                checked={item.controlled}
                onChange={(event) =>
                  edit("chronic_conditions", index, { ...item, controlled: event.target.checked })
                }
              />
              <Checkbox
                label="Medically cleared"
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
          title="Pain areas"
          emptyLabel="No pain areas declared"
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
              title={`Pain area ${index + 1}`}
              onRemove={() =>
                setData((value) => ({
                  ...value,
                  pain_areas: value.pain_areas.filter((_, itemIndex) => itemIndex !== index),
                }))
              }
            >
              <Input
                label="Area"
                required
                value={item.area}
                onChange={(event) =>
                  edit("pain_areas", index, { ...item, area: event.target.value })
                }
              />
              <Input
                label="Intensity (0–10)"
                type="number"
                min={0}
                max={10}
                value={item.intensity}
                onChange={(event) =>
                  edit("pain_areas", index, { ...item, intensity: Number(event.target.value) })
                }
              />
              <Checkbox
                label="Related to movement"
                checked={item.movement_related}
                onChange={(event) =>
                  edit("pain_areas", index, { ...item, movement_related: event.target.checked })
                }
              />
            </RecordCard>
          ))}
        </HealthGroup>
        <HealthGroup
          title="Mobility limitations"
          emptyLabel="No mobility limitations declared"
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
              title={`Limitation ${index + 1}`}
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
                label="Area"
                required
                value={item.area}
                onChange={(event) =>
                  edit("mobility_limitations", index, { ...item, area: event.target.value })
                }
              />
              <Textarea
                label="Description"
                required
                maxLength={300}
                value={item.description}
                onChange={(event) =>
                  edit("mobility_limitations", index, { ...item, description: event.target.value })
                }
              />
              <Select
                label="Severity"
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
          title="Surgery history"
          emptyLabel="No surgeries declared"
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
              title={`Surgery ${index + 1}`}
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
                label="Procedure"
                required
                value={item.procedure}
                onChange={(event) =>
                  edit("surgery_history", index, { ...item, procedure: event.target.value })
                }
              />
              <Input
                label="Surgery date"
                type="date"
                required
                max={new Date().toISOString().slice(0, 10)}
                value={item.surgery_date}
                onChange={(event) =>
                  edit("surgery_history", index, { ...item, surgery_date: event.target.value })
                }
              />
              <Checkbox
                label="Medically cleared"
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
            label="I confirm this declaration is accurate and complete"
            description="Empty sections explicitly mean that you have no records to declare in that category."
            checked={confirmed}
            onChange={(event) => setConfirmed(event.target.checked)}
          />
        </Card>
        <div className="iw-form-footer">
          <Button size="lg" type="submit" disabled={!confirmed} loading={saving}>
            Save health declaration
          </Button>
        </div>
      </form>
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
  count,
  onAdd,
  children,
}: {
  title: string;
  emptyLabel: string;
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
          Add {singular(title)}
        </Button>
      </fieldset>
    </Card>
  );
}

function singular(value: string): string {
  const known: Record<string, string> = {
    Injuries: "injury",
    "Chronic conditions": "chronic condition",
    "Pain areas": "pain area",
    "Mobility limitations": "mobility limitation",
    "Surgery history": "surgery",
  };
  return known[value] ?? value.toLowerCase();
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
  return (
    <section className="iw-record">
      <div className="iw-record-heading">
        <h3>{title}</h3>
        <Button type="button" variant="ghost" size="sm" onClick={onRemove}>
          Remove
        </Button>
      </div>
      <div className="iw-form-grid">{children}</div>
    </section>
  );
}
