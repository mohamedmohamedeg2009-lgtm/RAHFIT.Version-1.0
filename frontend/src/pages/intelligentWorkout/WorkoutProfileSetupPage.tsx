import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { label } from "../../components/intelligentWorkout/utils";
import { Button, Card, Checkbox, Input, Select } from "../../components/ui";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { Equipment, TrainingGoal, UserProfileRequest } from "../../types/intelligentWorkout";

const goals: TrainingGoal[] = [
  "fat_loss",
  "muscle_gain",
  "strength",
  "general_fitness",
  "endurance",
  "football_performance",
  "goalkeeper_performance",
];
const equipment: Equipment[] = [
  "barbell",
  "dumbbell",
  "machine",
  "cable",
  "resistance_band",
  "bodyweight",
  "kettlebell",
  "medicine_ball",
  "bench",
  "pull_up_bar",
  "cardio_machine",
];
const preferences = ["halal", "vegetarian", "vegan", "no_pork", "no_seafood"] as const;
const allergies = [
  "milk",
  "egg",
  "peanut",
  "tree_nut",
  "soy",
  "fish",
  "shellfish",
  "gluten",
] as const;

export default function WorkoutProfileSetupPage() {
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const [form, setForm] = useState({
    fullName: "",
    age: 18,
    gender: "prefer_not_to_say" as UserProfileRequest["identity"]["gender"],
    country: "",
    height: 170,
    weight: 70,
    bodyFat: "",
    primaryGoal: "general_fitness" as TrainingGoal,
    secondaryGoal: "",
    targetWeight: "",
    targetDate: "",
    experience: "beginner" as UserProfileRequest["training"]["experience"],
    availableDays: 3,
    sessionDuration: 45,
    workoutLocation: "commercial_gym" as UserProfileRequest["training"]["workout_location"],
    equipment: ["bodyweight"] as Equipment[],
    sleep: 8,
    stress: 5,
    activity: "moderate" as UserProfileRequest["lifestyle"]["activity_level"],
    water: 2000,
    preferences: [] as UserProfileRequest["nutrition"]["dietary_preferences"],
    allergies: [] as UserProfileRequest["nutrition"]["allergies"],
    restrictions: "",
  });
  const update = <K extends keyof typeof form>(key: K, value: (typeof form)[K]) =>
    setForm((current) => ({ ...current, [key]: value }));
  const toggle = <T extends string>(items: T[], item: T) =>
    items.includes(item) ? items.filter((value) => value !== item) : [...items, item];
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    const payload: UserProfileRequest = {
      identity: {
        full_name: form.fullName.trim(),
        age: form.age,
        gender: form.gender,
        country: form.country.trim().toUpperCase(),
      },
      body: {
        height_cm: form.height,
        weight_kg: form.weight,
        body_fat_percentage: form.bodyFat ? Number(form.bodyFat) : null,
      },
      goals: {
        primary_goal: form.primaryGoal,
        secondary_goal: form.secondaryGoal ? (form.secondaryGoal as TrainingGoal) : null,
        target_weight_kg: form.targetWeight ? Number(form.targetWeight) : null,
        target_date: form.targetDate || null,
      },
      training: {
        experience: form.experience,
        available_days: form.availableDays,
        session_duration_minutes: form.sessionDuration,
        available_equipment: form.equipment,
        workout_location: form.workoutLocation,
      },
      lifestyle: {
        sleep_hours: form.sleep,
        stress_level: form.stress,
        activity_level: form.activity,
        daily_water_ml: form.water,
      },
      nutrition: {
        dietary_preferences: form.preferences,
        allergies: form.allergies,
        dietary_restrictions: form.restrictions
          .split(",")
          .map((value) => value.trim())
          .filter(Boolean),
      },
    };
    try {
      await intelligentWorkoutService.updateProfile(payload);
      navigate("/intelligent-workouts/setup/health", { state: { profileSaved: true } });
    } catch (cause) {
      setError(mapWorkoutError(cause));
    } finally {
      setSaving(false);
    }
  };
  return (
    <IntelligentWorkoutShell
      title="Training profile"
      description="Provide the source information the backend needs to make safe, personalized workout decisions."
    >
      {error ? <WorkoutErrorAlert error={error} /> : null}
      <form className="iw-setup-form" onSubmit={(event) => void submit(event)}>
        <Card>
          <fieldset>
            <legend>Identity</legend>
            <div className="iw-form-grid">
              <Input
                label="Full name"
                required
                minLength={2}
                maxLength={120}
                value={form.fullName}
                onChange={(event) => update("fullName", event.target.value)}
              />
              <Input
                label="Age"
                required
                type="number"
                min={13}
                max={100}
                value={form.age}
                onChange={(event) => update("age", Number(event.target.value))}
              />
              <Select
                label="Gender"
                value={form.gender}
                onChange={(event) => update("gender", event.target.value as typeof form.gender)}
                options={["male", "female", "non_binary", "prefer_not_to_say"].map(option)}
              />
              <Input
                label="Country code"
                hint="Two-letter ISO code, for example EG or KW"
                required
                minLength={2}
                maxLength={2}
                value={form.country}
                onChange={(event) => update("country", event.target.value)}
              />
            </div>
          </fieldset>
        </Card>
        <Card>
          <fieldset>
            <legend>Body</legend>
            <div className="iw-form-grid">
              <Input
                label="Height (cm)"
                required
                type="number"
                min={100}
                max={250}
                step="0.1"
                value={form.height}
                onChange={(event) => update("height", Number(event.target.value))}
              />
              <Input
                label="Weight (kg)"
                required
                type="number"
                min={30}
                max={350}
                step="0.1"
                value={form.weight}
                onChange={(event) => update("weight", Number(event.target.value))}
              />
              <Input
                label="Body fat % (optional)"
                type="number"
                min={2}
                max={70}
                step="0.1"
                value={form.bodyFat}
                onChange={(event) => update("bodyFat", event.target.value)}
              />
            </div>
          </fieldset>
        </Card>
        <Card>
          <fieldset>
            <legend>Goals</legend>
            <div className="iw-form-grid">
              <Select
                label="Primary goal"
                value={form.primaryGoal}
                onChange={(event) => update("primaryGoal", event.target.value as TrainingGoal)}
                options={goals.map(option)}
              />
              <Select
                label="Secondary goal (optional)"
                value={form.secondaryGoal}
                onChange={(event) => update("secondaryGoal", event.target.value)}
                options={[
                  { label: "None", value: "" },
                  ...goals.filter((goal) => goal !== form.primaryGoal).map(option),
                ]}
              />
              <Input
                label="Target weight (kg)"
                type="number"
                min={30}
                max={350}
                step="0.1"
                value={form.targetWeight}
                onChange={(event) => update("targetWeight", event.target.value)}
              />
              <Input
                label="Target date"
                type="date"
                value={form.targetDate}
                onChange={(event) => update("targetDate", event.target.value)}
              />
            </div>
            <p className="ds-field-hint">
              Target weight and target date must be supplied together.
            </p>
          </fieldset>
        </Card>
        <Card>
          <fieldset>
            <legend>Training</legend>
            <div className="iw-form-grid">
              <Select
                label="Experience"
                value={form.experience}
                onChange={(event) =>
                  update("experience", event.target.value as typeof form.experience)
                }
                options={["beginner", "intermediate", "advanced"].map(option)}
              />
              <Input
                label="Available days / week"
                type="number"
                min={1}
                max={7}
                value={form.availableDays}
                onChange={(event) => update("availableDays", Number(event.target.value))}
              />
              <Input
                label="Session duration (minutes)"
                type="number"
                min={15}
                max={180}
                value={form.sessionDuration}
                onChange={(event) => update("sessionDuration", Number(event.target.value))}
              />
              <Select
                label="Workout location"
                value={form.workoutLocation}
                onChange={(event) =>
                  update("workoutLocation", event.target.value as typeof form.workoutLocation)
                }
                options={["commercial_gym", "home_gym", "bodyweight_only", "outdoor"].map(option)}
              />
            </div>
            <div className="iw-choice-grid" role="group" aria-label="Available equipment">
              {equipment.map((item) => (
                <Checkbox
                  key={item}
                  label={label(item)}
                  checked={form.equipment.includes(item)}
                  onChange={() => update("equipment", toggle(form.equipment, item))}
                />
              ))}
            </div>
          </fieldset>
        </Card>
        <Card>
          <fieldset>
            <legend>Lifestyle and nutrition</legend>
            <div className="iw-form-grid">
              <Input
                label="Sleep (hours)"
                type="number"
                min={0}
                max={24}
                step="0.5"
                value={form.sleep}
                onChange={(event) => update("sleep", Number(event.target.value))}
              />
              <Input
                label="Stress level (1–10)"
                type="number"
                min={1}
                max={10}
                value={form.stress}
                onChange={(event) => update("stress", Number(event.target.value))}
              />
              <Select
                label="Activity level"
                value={form.activity}
                onChange={(event) => update("activity", event.target.value as typeof form.activity)}
                options={["sedentary", "light", "moderate", "very_active", "extra_active"].map(
                  option,
                )}
              />
              <Input
                label="Daily water (ml)"
                type="number"
                min={0}
                max={10000}
                value={form.water}
                onChange={(event) => update("water", Number(event.target.value))}
              />
            </div>
            <h3>Dietary preferences</h3>
            <div className="iw-choice-grid">
              {preferences.map((item) => (
                <Checkbox
                  key={item}
                  label={label(item)}
                  checked={form.preferences.includes(item)}
                  onChange={() => update("preferences", toggle([...form.preferences], item))}
                />
              ))}
            </div>
            <h3>Allergies</h3>
            <div className="iw-choice-grid">
              {allergies.map((item) => (
                <Checkbox
                  key={item}
                  label={label(item)}
                  checked={form.allergies.includes(item)}
                  onChange={() => update("allergies", toggle([...form.allergies], item))}
                />
              ))}
            </div>
            <Input
              label="Other dietary restrictions"
              hint="Comma-separated; leave blank if none"
              value={form.restrictions}
              onChange={(event) => update("restrictions", event.target.value)}
            />
          </fieldset>
        </Card>
        <div className="iw-form-footer">
          <Button size="lg" loading={saving} type="submit">
            Save and continue
          </Button>
        </div>
      </form>
    </IntelligentWorkoutShell>
  );
}

const option = (value: string) => ({ value, label: label(value) });
