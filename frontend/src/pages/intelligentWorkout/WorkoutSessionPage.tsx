import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  AdaptationResult,
  IntelligentWorkoutShell,
  SessionStatusCard,
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
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type {
  CompletedExerciseInput,
  PlannedExercise,
  SessionStatus,
  WorkoutAdaptationResponse,
  WorkoutPlanResponse,
  WorkoutSessionResponse,
} from "../../types/intelligentWorkout";
import { useLocale } from "../../contexts/LocaleContext";
import { workoutEnumLabel, workoutText } from "../../i18n/intelligentWorkout";

export default function IntelligentWorkoutSessionPage() {
  const { locale } = useLocale();
  const t = (key: Parameters<typeof workoutText>[1]) => workoutText(locale, key);
  const label = (value: string) => workoutEnumLabel(value, locale);
  const { planId = "", dayNumber = "", sessionId = "" } = useParams();
  const [plan, setPlan] = useState<WorkoutPlanResponse | null>(null);
  const [session, setSession] = useState<WorkoutSessionResponse | null>(null);
  const [entries, setEntries] = useState<CompletedExerciseInput[]>([]);
  const [notes, setNotes] = useState("");
  const [duration, setDuration] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const [adaptation, setAdaptation] = useState<WorkoutAdaptationResponse | null>(null);
  const selectedDayNumber = session?.day_number ?? Number(dayNumber);
  const day = useMemo(
    () => plan?.weekly_schedule.find((item) => item.day_number === selectedDayNumber) ?? null,
    [plan, selectedDayNumber],
  );
  const exercises = useMemo(
    () => day?.sections.flatMap((section) => section.exercises) ?? [],
    [day],
  );

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const loadedSession = sessionId
        ? await intelligentWorkoutService.getSession(sessionId)
        : null;
      const loadedPlan = await intelligentWorkoutService.getPlan(loadedSession?.plan_id ?? planId);
      setSession(loadedSession);
      setPlan(loadedPlan);
      setDuration(loadedSession?.actual_duration_minutes?.toString() ?? "");
      const planned =
        loadedPlan.weekly_schedule
          .find((item) => item.day_number === (loadedSession?.day_number ?? Number(dayNumber)))
          ?.sections.flatMap((section) => section.exercises) ?? [];
      setEntries(
        planned.map((exercise) =>
          mergeEntry(
            exercise,
            loadedSession?.completed_exercises.find(
              (entry) => entry.exercise_id === exercise.exercise_id,
            ),
          ),
        ),
      );
    } catch (cause) {
      setError(mapWorkoutError(cause, locale));
    } finally {
      setLoading(false);
    }
  }, [dayNumber, locale, planId, sessionId]);
  useEffect(() => {
    // Initial route loading synchronizes the protected screen with its server resource.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  const start = async () => {
    if (!plan || !day || saving) return;
    setSaving(true);
    setError(null);
    try {
      const created = await intelligentWorkoutService.createSession({
        plan_id: plan.plan_id,
        day_number: day.day_number,
        status: "in_progress",
        completed_exercises: [],
      });
      setSession(created);
      setEntries(
        day.sections
          .flatMap((section) => section.exercises)
          .map((exercise) => mergeEntry(exercise)),
      );
    } catch (cause) {
      setError(mapWorkoutError(cause, locale));
    } finally {
      setSaving(false);
    }
  };

  const save = async (status: SessionStatus = "in_progress") => {
    if (!session) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await intelligentWorkoutService.updateSession(session.session_id, {
        status,
        completed_exercises: entries,
        actual_duration_minutes: duration ? Number(duration) : null,
        notes: notes.trim() || null,
      });
      setSession(updated);
    } catch (cause) {
      setError(mapWorkoutError(cause, locale));
    } finally {
      setSaving(false);
    }
  };
  const analyze = async () => {
    if (!session) return;
    setSaving(true);
    setError(null);
    try {
      setAdaptation(await intelligentWorkoutService.analyzeAdaptation(session.plan_id));
    } catch (cause) {
      setError(mapWorkoutError(cause, locale));
    } finally {
      setSaving(false);
    }
  };
  const updateEntry = (
    exerciseId: string,
    transform: (entry: CompletedExerciseInput) => CompletedExerciseInput,
  ) =>
    setEntries((current) =>
      current.map((entry) => (entry.exercise_id === exerciseId ? transform(entry) : entry)),
    );

  return (
    <IntelligentWorkoutShell
      title={day?.title ?? t("workoutSession")}
      description={t("sessionDescription")}
    >
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void load()} /> : null}
      {loading ? (
        <Card aria-live="polite" aria-busy="true">
          <span className="sr-only">{t("loadingSession")}</span>
          <Skeleton height="14rem" />
        </Card>
      ) : plan && day && !session ? (
        <Card className="iw-form-card">
          <h2>{day.title}</h2>
          <p>
            {day.focus} ·{" "}
            {workoutText(locale, "minutes", { count: day.estimated_duration_minutes })} ·{" "}
            {workoutText(locale, "exerciseCount", {
              count: day.sections.reduce(
                (count, section) => count + section.exercises.length,
                0,
              ),
            })}
          </p>
          <Alert variant="info" title={t("readyToBegin")}>
            <p>{t("readyToBeginDescription")}</p>
          </Alert>
          <Button size="lg" loading={saving} onClick={() => void start()}>
            {t("startWorkoutSession")}
          </Button>
        </Card>
      ) : session && day ? (
        <>
          <SessionStatusCard session={session} />
          {session.adaptation_flags.length ? (
            <Alert variant="warning" title={t("reviewRecommended")}>
              <ul>
                {session.adaptation_flags.map((flag) => (
                  <li key={flag}>{label(flag)}</li>
                ))}
              </ul>
            </Alert>
          ) : null}
          {session.status !== "in_progress" ? (
            <Alert
              variant={session.status === "completed" ? "success" : "warning"}
              title={workoutText(locale, "sessionState", {
                status: workoutEnumLabel(session.status, locale),
              })}
            >
              <p>{t("sessionReadOnly")}</p>
            </Alert>
          ) : null}
          <div className="iw-session-exercises">
            {exercises.map((exercise) => {
              const entry = entries.find((item) => item.exercise_id === exercise.exercise_id);
              if (!entry) return null;
              return (
                <Card className="iw-session-exercise" key={exercise.exercise_id}>
                  <header>
                    <div>
                      <h2>{exercise.exercise_name}</h2>
                      <p>
                        {exercise.prescription.sets} {t("sets")} · {exercise.prescription.min_reps}–
                        {exercise.prescription.max_reps} {t("reps")} · RPE{" "}
                        {exercise.prescription.rpe_min}–{exercise.prescription.rpe_max}
                      </p>
                    </div>
                    <Checkbox
                      label={t("skipExercise")}
                      checked={entry.skipped ?? false}
                      disabled={session.status !== "in_progress"}
                      onChange={(event) =>
                        updateEntry(exercise.exercise_id, (value) => ({
                          ...value,
                          skipped: event.target.checked,
                        }))
                      }
                    />
                  </header>
                  <p>{exercise.prescription.intensity_guidance}</p>
                  <div
                    className="iw-set-table"
                    role="group"
                    aria-label={workoutText(locale, "exerciseSets", {
                      name: exercise.exercise_name,
                    })}
                  >
                    {entry.completed_sets.map((set, setIndex) => (
                      <div className="iw-set-row" key={set.set_number}>
                        <strong>
                          {workoutText(locale, "setNumber", { count: set.set_number })}
                        </strong>
                        <Checkbox
                          label={t("completed")}
                          checked={set.completed}
                          disabled={session.status !== "in_progress" || entry.skipped}
                          onChange={(event) =>
                            updateEntry(exercise.exercise_id, (value) => ({
                              ...value,
                              completed_sets: value.completed_sets.map((item, index) =>
                                index === setIndex
                                  ? { ...item, completed: event.target.checked }
                                  : item,
                              ),
                            }))
                          }
                        />
                        <Input
                          aria-label={workoutText(locale, "setRepetitions", {
                            count: set.set_number,
                          })}
                          label={t("reps")}
                          type="number"
                          min={0}
                          max={100}
                          disabled={session.status !== "in_progress" || entry.skipped}
                          value={set.actual_reps ?? ""}
                          onChange={(event) =>
                            updateSet(
                              exercise.exercise_id,
                              setIndex,
                              "actual_reps",
                              event.target.value,
                            )
                          }
                        />
                        <Input
                          aria-label={workoutText(locale, "setLoad", { count: set.set_number })}
                          label={t("loadKg")}
                          type="number"
                          min={0}
                          max={1000}
                          step="0.5"
                          disabled={session.status !== "in_progress" || entry.skipped}
                          value={set.actual_load_kg ?? ""}
                          onChange={(event) =>
                            updateSet(
                              exercise.exercise_id,
                              setIndex,
                              "actual_load_kg",
                              event.target.value,
                            )
                          }
                        />
                        <Select
                          aria-label={workoutText(locale, "setExertion", {
                            count: set.set_number,
                          })}
                          label="RPE"
                          disabled={session.status !== "in_progress" || entry.skipped}
                          value={set.perceived_exertion ?? ""}
                          onChange={(event) =>
                            updateSet(
                              exercise.exercise_id,
                              setIndex,
                              "perceived_exertion",
                              event.target.value,
                            )
                          }
                          options={[
                            { value: "", label: t("notSet") },
                            ...Array.from({ length: 10 }, (_, index) => ({
                              value: String(index + 1),
                              label: String(index + 1),
                            })),
                          ]}
                        />
                      </div>
                    ))}
                  </div>
                  <div className="iw-pain-fields">
                    <Checkbox
                      label={t("painExperienced")}
                      checked={entry.pain_reported ?? false}
                      disabled={session.status !== "in_progress"}
                      onChange={(event) =>
                        updateEntry(exercise.exercise_id, (value) => ({
                          ...value,
                          pain_reported: event.target.checked,
                          pain_area: event.target.checked ? value.pain_area : null,
                        }))
                      }
                    />
                    {entry.pain_reported ? (
                      <Input
                        label={t("painArea")}
                        required
                        maxLength={80}
                        disabled={session.status !== "in_progress"}
                        value={entry.pain_area ?? ""}
                        onChange={(event) =>
                          updateEntry(exercise.exercise_id, (value) => ({
                            ...value,
                            pain_area: event.target.value,
                          }))
                        }
                      />
                    ) : null}
                  </div>
                </Card>
              );
            })}
          </div>
          <Card className="iw-session-notes">
            <Input
              label={t("actualDuration")}
              type="number"
              min={1}
              max={300}
              disabled={session.status !== "in_progress"}
              value={duration}
              onChange={(event) => setDuration(event.target.value)}
            />
            <Textarea
              label={t("sessionNotes")}
              maxLength={1000}
              disabled={session.status !== "in_progress"}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </Card>
          {adaptation ? <AdaptationResult result={adaptation} /> : null}
          <div className="iw-actions iw-sticky-actions">
            {session.status === "in_progress" ? (
              <>
                <Button loading={saving} variant="outline" onClick={() => void save()}>
                  {t("saveProgress")}
                </Button>
                <Button loading={saving} onClick={() => void save("completed")}>
                  {t("completeSession")}
                </Button>
                <Button loading={saving} variant="danger" onClick={() => void save("abandoned")}>
                  {t("abandon")}
                </Button>
              </>
            ) : null}
            <Button loading={saving} variant="ghost" onClick={() => void analyze()}>
              {t("analyzeAdaptation")}
            </Button>
            <Link
              className="ds-button ds-button-ghost ds-button-md"
              to="/intelligent-workouts/history/sessions"
            >
              {t("sessionHistory")}
            </Link>
          </div>
        </>
      ) : null}
    </IntelligentWorkoutShell>
  );

  function updateSet(
    exerciseId: string,
    setIndex: number,
    key: "actual_reps" | "actual_load_kg" | "perceived_exertion",
    raw: string,
  ) {
    updateEntry(exerciseId, (entry) => ({
      ...entry,
      completed_sets: entry.completed_sets.map((set, index) =>
        index === setIndex ? { ...set, [key]: raw === "" ? null : Number(raw) } : set,
      ),
    }));
  }
}

function mergeEntry(
  exercise: PlannedExercise,
  stored?: CompletedExerciseInput,
): CompletedExerciseInput {
  return {
    exercise_id: exercise.exercise_id,
    skipped: stored?.skipped ?? false,
    pain_reported: stored?.pain_reported ?? false,
    pain_area: stored?.pain_area ?? null,
    completed_sets: Array.from(
      { length: exercise.prescription.sets },
      (_, index) =>
        stored?.completed_sets.find((set) => set.set_number === index + 1) ?? {
          set_number: index + 1,
          completed: false,
        },
    ),
  };
}
