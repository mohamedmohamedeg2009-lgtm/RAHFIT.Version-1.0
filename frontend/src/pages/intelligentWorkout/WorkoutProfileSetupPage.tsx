import { useEffect, useRef, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { Alert, Button, Card, Checkbox, Input, Select, Skeleton } from "../../components/ui";
import { ApiError } from "../../services/apiClient";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { Equipment, TrainingGoal, UserProfileRequest } from "../../types/intelligentWorkout";
import { useLocale } from "../../contexts/LocaleContext";
import { workoutEnumLabel, workoutText } from "../../i18n/intelligentWorkout";
import { isAllowedValue, validateNumber, validateRequiredText } from "../../utils/formValidation";

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
const defaultForm = {
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
};
type ProfileForm = typeof defaultForm;

export default function WorkoutProfileSetupPage() {
  const { locale } = useLocale();
  const t = (key: Parameters<typeof workoutText>[1]) => workoutText(locale, key);
  const option = (value: string) => ({ value, label: workoutEnumLabel(value, locale) });
  const navigate = useNavigate();
  const dirty = useRef(false);
  const [loading, setLoading] = useState(true);
  const [hasExisting, setHasExisting] = useState<boolean | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [form, setForm] = useState<ProfileForm>(defaultForm);
  useEffect(() => {
    let active = true;
    void intelligentWorkoutService
      .getProfile()
      .then((profile) => {
        if (!active) return;
        setHasExisting(true);
        if (!dirty.current) setForm(profileToForm(profile));
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
  const update = <K extends keyof typeof form>(key: K, value: (typeof form)[K]) =>
    setForm((current) => {
      dirty.current = true;
      return { ...current, [key]: value };
    });
  const toggle = <T extends string>(items: T[], item: T) =>
    items.includes(item) ? items.filter((value) => value !== item) : [...items, item];
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const validationMessage = validateProfile(form);
    if (validationMessage) {
      setValidationError(validationMessage);
      return;
    }
    setSaving(true);
    setError(null);
    setValidationError(null);
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
      await intelligentWorkoutService.getProfile();
      navigate("/intelligent-workouts/setup/health", { state: { profileSaved: true } });
    } catch (cause) {
      setError(mapWorkoutError(cause, locale));
    } finally {
      setSaving(false);
    }
  };
  return (
    <IntelligentWorkoutShell title={t("profileTitle")} description={t("profileDescription")}>
      {error ? <WorkoutErrorAlert error={error} /> : null}
      {validationError ? <Alert variant="danger" title={t("profileTitle")}><p>{validationError}</p></Alert> : null}
      {loading ? (
        <Card aria-live="polite" aria-busy="true">
          <span className="sr-only">{t("loadingSavedProfile")}</span>
          <Skeleton height="12rem" />
        </Card>
      ) : (
        <>
          {hasExisting === false ? (
            <Alert variant="info" title={t("noSavedProfile")}>
              <p>{t("noSavedProfileDescription")}</p>
            </Alert>
          ) : hasExisting ? (
            <Alert variant="success" title={t("savedProfileLoaded")}>
              <p>{t("savedProfileLoadedDescription")}</p>
            </Alert>
          ) : null}
          <form className="iw-setup-form" onSubmit={(event) => void submit(event)}>
            <Card>
              <fieldset>
                <legend>{t("identity")}</legend>
                <div className="iw-form-grid">
                  <Input
                    label={t("fullName")}
                    required
                    minLength={2}
                    maxLength={120}
                    value={form.fullName}
                    onChange={(event) => update("fullName", event.target.value)}
                  />
                  <Input
                    label={t("age")}
                    required
                    type="number"
                    min={13}
                    max={100}
                    value={form.age}
                    onChange={(event) => update("age", Number(event.target.value))}
                  />
                  <Select
                    label={t("gender")}
                    value={form.gender}
                    onChange={(event) => update("gender", event.target.value as typeof form.gender)}
                    options={["male", "female", "non_binary", "prefer_not_to_say"].map(option)}
                  />
                  <Input
                    label={t("countryCode")}
                    hint={t("countryHint")}
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
                <legend>{t("body")}</legend>
                <div className="iw-form-grid">
                  <Input
                    label={t("height")}
                    required
                    type="number"
                    min={100}
                    max={250}
                    step="0.1"
                    value={form.height}
                    onChange={(event) => update("height", Number(event.target.value))}
                  />
                  <Input
                    label={t("weight")}
                    required
                    type="number"
                    min={30}
                    max={350}
                    step="0.1"
                    value={form.weight}
                    onChange={(event) => update("weight", Number(event.target.value))}
                  />
                  <Input
                    label={t("bodyFat")}
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
                <legend>{t("goals")}</legend>
                <div className="iw-form-grid">
                  <Select
                    label={t("primaryGoal")}
                    value={form.primaryGoal}
                    onChange={(event) => update("primaryGoal", event.target.value as TrainingGoal)}
                    options={goals.map(option)}
                  />
                  <Select
                    label={t("secondaryGoal")}
                    value={form.secondaryGoal}
                    onChange={(event) => update("secondaryGoal", event.target.value)}
                    options={[
                      { label: t("none"), value: "" },
                      ...goals.filter((goal) => goal !== form.primaryGoal).map(option),
                    ]}
                  />
                  <Input
                    label={t("targetWeight")}
                    type="number"
                    min={30}
                    max={350}
                    step="0.1"
                    value={form.targetWeight}
                    onChange={(event) => update("targetWeight", event.target.value)}
                  />
                  <Input
                    label={t("targetDate")}
                    type="date"
                    value={form.targetDate}
                    onChange={(event) => update("targetDate", event.target.value)}
                  />
                </div>
                <p className="ds-field-hint">{t("targetPairHint")}</p>
              </fieldset>
            </Card>
            <Card>
              <fieldset>
                <legend>{t("training")}</legend>
                <div className="iw-form-grid">
                  <Select
                    label={t("experience")}
                    value={form.experience}
                    onChange={(event) =>
                      update("experience", event.target.value as typeof form.experience)
                    }
                    options={["beginner", "intermediate", "advanced"].map(option)}
                  />
                  <Input
                    label={t("availableDays")}
                    type="number"
                    min={1}
                    max={7}
                    value={form.availableDays}
                    onChange={(event) => update("availableDays", Number(event.target.value))}
                  />
                  <Input
                    label={t("sessionDuration")}
                    type="number"
                    min={15}
                    max={180}
                    value={form.sessionDuration}
                    onChange={(event) => update("sessionDuration", Number(event.target.value))}
                  />
                  <Select
                    label={t("workoutLocation")}
                    value={form.workoutLocation}
                    onChange={(event) =>
                      update("workoutLocation", event.target.value as typeof form.workoutLocation)
                    }
                    options={["commercial_gym", "home_gym", "bodyweight_only", "outdoor"].map(
                      option,
                    )}
                  />
                </div>
                <div className="iw-choice-grid" role="group" aria-label={t("availableEquipment")}>
                  {equipment.map((item) => (
                    <Checkbox
                      key={item}
                      label={workoutEnumLabel(item, locale)}
                      checked={form.equipment.includes(item)}
                      onChange={() => update("equipment", toggle(form.equipment, item))}
                    />
                  ))}
                </div>
              </fieldset>
            </Card>
            <Card>
              <fieldset>
                <legend>{t("lifestyleNutrition")}</legend>
                <div className="iw-form-grid">
                  <Input
                    label={t("sleep")}
                    type="number"
                    min={0}
                    max={24}
                    step="0.5"
                    value={form.sleep}
                    onChange={(event) => update("sleep", Number(event.target.value))}
                  />
                  <Input
                    label={t("stress")}
                    type="number"
                    min={1}
                    max={10}
                    value={form.stress}
                    onChange={(event) => update("stress", Number(event.target.value))}
                  />
                  <Select
                    label={t("activityLevel")}
                    value={form.activity}
                    onChange={(event) =>
                      update("activity", event.target.value as typeof form.activity)
                    }
                    options={["sedentary", "light", "moderate", "very_active", "extra_active"].map(
                      option,
                    )}
                  />
                  <Input
                    label={t("dailyWater")}
                    type="number"
                    min={0}
                    max={10000}
                    value={form.water}
                    onChange={(event) => update("water", Number(event.target.value))}
                  />
                </div>
                <h3>{t("dietaryPreferences")}</h3>
                <div className="iw-choice-grid">
                  {preferences.map((item) => (
                    <Checkbox
                      key={item}
                      label={workoutEnumLabel(item, locale)}
                      checked={form.preferences.includes(item)}
                      onChange={() => update("preferences", toggle([...form.preferences], item))}
                    />
                  ))}
                </div>
                <h3>{t("allergies")}</h3>
                <div className="iw-choice-grid">
                  {allergies.map((item) => (
                    <Checkbox
                      key={item}
                      label={workoutEnumLabel(item, locale)}
                      checked={form.allergies.includes(item)}
                      onChange={() => update("allergies", toggle([...form.allergies], item))}
                    />
                  ))}
                </div>
                <Input
                  label={t("otherRestrictions")}
                  hint={t("restrictionsHint")}
                  value={form.restrictions}
                  onChange={(event) => update("restrictions", event.target.value)}
                />
              </fieldset>
            </Card>
            <div className="iw-form-footer">
              <Button size="lg" loading={saving} type="submit">
                {t("saveContinue")}
              </Button>
            </div>
          </form>
        </>
      )}
    </IntelligentWorkoutShell>
  );
}

function validateProfile(form: ProfileForm): string | undefined {
  const requiredText = [
    validateRequiredText(form.fullName, "Full name", { min: 2, max: 120 }),
    validateRequiredText(form.country, "Country code", { min: 2, max: 2 }),
  ].find(Boolean);
  if (requiredText) return requiredText;
  const numberErrors = [
    validateNumber(form.age, "Age", 13, 100),
    validateNumber(form.height, "Height", 100, 250),
    validateNumber(form.weight, "Weight", 30, 350),
    validateNumber(form.availableDays, "Available days", 1, 7),
    validateNumber(form.sessionDuration, "Session duration", 15, 180),
    validateNumber(form.sleep, "Sleep", 0, 24),
    validateNumber(form.stress, "Stress", 1, 10),
    validateNumber(form.water, "Daily water", 0, 10000),
  ].find(Boolean);
  if (numberErrors) return numberErrors;
  if (form.bodyFat && validateNumber(form.bodyFat, "Body fat", 2, 70)) return validateNumber(form.bodyFat, "Body fat", 2, 70);
  if (form.targetWeight && validateNumber(form.targetWeight, "Target weight", 30, 350)) return validateNumber(form.targetWeight, "Target weight", 30, 350);
  if (!isAllowedValue(form.primaryGoal, goals) || !isAllowedValue(form.experience, ["beginner", "intermediate", "advanced"] as const)) return "Choose a valid training preference.";
  if (!form.equipment.length || form.equipment.some((item) => !isAllowedValue(item, equipment))) return "Select at least one available equipment option.";
  return undefined;
}

function profileToForm(profile: UserProfileRequest): ProfileForm {
  return {
    fullName: profile.identity.full_name,
    age: profile.identity.age,
    gender: profile.identity.gender,
    country: profile.identity.country,
    height: profile.body.height_cm,
    weight: profile.body.weight_kg,
    bodyFat: profile.body.body_fat_percentage?.toString() ?? "",
    primaryGoal: profile.goals.primary_goal,
    secondaryGoal: profile.goals.secondary_goal ?? "",
    targetWeight: profile.goals.target_weight_kg?.toString() ?? "",
    targetDate: profile.goals.target_date ?? "",
    experience: profile.training.experience,
    availableDays: profile.training.available_days,
    sessionDuration: profile.training.session_duration_minutes,
    workoutLocation: profile.training.workout_location,
    equipment: [...profile.training.available_equipment],
    sleep: profile.lifestyle.sleep_hours,
    stress: profile.lifestyle.stress_level,
    activity: profile.lifestyle.activity_level,
    water: profile.lifestyle.daily_water_ml,
    preferences: [...profile.nutrition.dietary_preferences],
    allergies: [...profile.nutrition.allergies],
    restrictions: profile.nutrition.dietary_restrictions.join(", "),
  };
}
