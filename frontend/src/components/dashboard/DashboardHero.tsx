import { motion } from "framer-motion";
import { Droplet, Flame, BarChart3 } from "lucide-react";
import type { DashboardSummaryData } from "../../types/dashboard";
import type { Locale } from "../../contexts/LocaleContext";

interface DashboardHeroProps {
  data: DashboardSummaryData;
  locale: Locale;
}

function CircularProgressRing({
  value,
  max = 100,
  color,
  size = 84,
  strokeWidth = 7,
}: {
  value: number;
  max?: number;
  color: string;
  size?: number;
  strokeWidth?: number;
}) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="ring-container" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle
          stroke="var(--color-border)"
          fill="transparent"
          strokeWidth={strokeWidth}
          r={radius}
          cx={size / 2}
          cy={size / 2}
          style={{ opacity: 0.3 }}
        />
        <motion.circle
          stroke={color}
          fill="transparent"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          strokeLinecap="round"
          r={radius}
          cx={size / 2}
          cy={size / 2}
          style={{ transform: "rotate(-90deg)", transformOrigin: "50% 50%" }}
        />
      </svg>
      <span className="ring-text" style={{ fontSize: "1.1rem" }}>
        {Math.round(percentage)}%
      </span>
    </div>
  );
}

export function DashboardHero({ data, locale }: DashboardHeroProps) {
  const { user, assessment, nutrition, latestCheckIn, workout } = data;

  const currentHour = new Date().getHours();
  let greeting: string;
  if (locale === "ar") {
    greeting = currentHour < 12 ? "صباح الخير" : "طاب مساؤك";
  } else {
    greeting = currentHour < 12 ? "Good morning" : "Good afternoon";
  }

  const readinessScore = latestCheckIn?.readinessScore ?? assessment.readinessScore;

  const labels = {
    en: {
      healthScore: "Health Score",
      recovery: "Recovery",
      sleep: "Sleep",
      hydration: "Hydration",
      nutrition: "Nutrition",
      workoutToday: "Workout Today",
      weeklyProgress: "Weekly Progress",
      noWorkout: "Rest Day",
      completed: "Completed",
      calories: "Calories",
      water: "Water",
      subtitle: "Here is your premium athletic overview based on verified safety gates.",
      weekDays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    ar: {
      healthScore: "مؤشر الصحة",
      recovery: "الاستشفاء",
      sleep: "النوم",
      hydration: "الترطيب",
      nutrition: "التغذية",
      workoutToday: "تمرين اليوم",
      weeklyProgress: "التقدم الأسبوعي",
      noWorkout: "يوم راحة",
      completed: "مكتمل",
      calories: "السعرات",
      water: "المياه",
      subtitle: "إليك نظرتك العامة الرياضية الممتازة المبنية على بوابات السلامة المعتمدة.",
      weekDays: ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"],
    },
  }[locale];

  return (
    <motion.div
      className="dashboard-hero-overview"
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <div className="dashboard-hero-content">
        <div>
          <h1 className="dashboard-hero-greeting">
            {greeting}, <span>{user.displayName}</span>
          </h1>
          <p className="dashboard-hero-subtitle">{labels.subtitle}</p>
        </div>

        <div className="dashboard-hero-grid">
          {readinessScore !== null && readinessScore !== undefined ? (
            <div className="dashboard-hero-ring-card">
              <span className="dashboard-hero-ring-title">{labels.healthScore}</span>
              <CircularProgressRing value={readinessScore} color="var(--color-primary)" />
            </div>
          ) : (
            <div className="dashboard-hero-ring-card">
              <span className="dashboard-hero-ring-title">{labels.healthScore}</span>
              <span>No check-in recorded yet</span>
            </div>
          )}
          {workout?.completionPercentage !== null &&
            workout?.completionPercentage !== undefined && (
              <div className="dashboard-hero-ring-card">
                <span className="dashboard-hero-ring-title">{labels.workoutToday}</span>
                <CircularProgressRing
                  value={workout.completionPercentage}
                  color="var(--color-accent)"
                />
              </div>
            )}
        </div>
      </div>

      <div className="dashboard-hero-metrics-side">
        {/* Hydration */}
        <div className="dashboard-hero-metric-box">
          <span className="dashboard-hero-metric-box-title">
            <Droplet size={18} color="var(--color-accent)" />
            {labels.hydration}
          </span>
          <div className="dashboard-hero-metric-box-value">
            {nutrition?.waterConsumedMl ?? "—"}{" "}
            <span style={{ fontSize: "14px", fontWeight: 500 }}>ml</span>
          </div>
          <span className="dashboard-hero-metric-box-sub">
            {nutrition?.waterTargetMl !== null && nutrition?.waterTargetMl !== undefined
              ? `/ ${nutrition.waterTargetMl} ml ${labels.water}`
              : "No hydration target recorded"}
          </span>
        </div>

        {/* Nutrition */}
        <div className="dashboard-hero-metric-box">
          <span className="dashboard-hero-metric-box-title">
            <Flame size={18} color="var(--color-danger)" />
            {labels.nutrition}
          </span>
          <div className="dashboard-hero-metric-box-value">
            {nutrition?.caloriesConsumed ?? "—"}{" "}
            <span style={{ fontSize: "14px", fontWeight: 500 }}>kcal</span>
          </div>
          <span className="dashboard-hero-metric-box-sub">
            {nutrition?.targetCalories !== null && nutrition?.targetCalories !== undefined
              ? `${labels.calories}: ${nutrition?.caloriesConsumed ?? "—"} / ${nutrition.targetCalories}`
              : "No calorie target recorded"}
          </span>
        </div>

        {/* Weekly Progress bar indicators */}
        <div className="dashboard-weekly-progress">
          <span className="dashboard-hero-metric-box-title">
            <BarChart3 size={18} color="var(--color-primary)" />
            {labels.weeklyProgress}
          </span>
          <div className="weekly-bars-container">
            <span>{workout ? `${workout.status}` : "No workouts recorded yet"}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
