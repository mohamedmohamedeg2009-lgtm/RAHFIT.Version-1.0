import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}
export function Card({ children, className = "", ...props }: CardProps) {
  return (
    <div className={`ds-card ${className}`} {...props}>
      {children}
    </div>
  );
}

function VariantCard({
  variant,
  children,
  className = "",
  ...props
}: CardProps & { variant: string }) {
  return (
    <Card className={`ds-card-${variant} ${className}`} {...props}>
      {children}
    </Card>
  );
}
export function MetricCard(props: CardProps) {
  return <VariantCard variant="metric" {...props} />;
}
export function ProfileCard(props: CardProps) {
  return <VariantCard variant="profile" {...props} />;
}
export function WorkoutCard(props: CardProps) {
  return <VariantCard variant="workout" {...props} />;
}
export function NutritionCard(props: CardProps) {
  return <VariantCard variant="nutrition" {...props} />;
}
export function AICoachCard(props: CardProps) {
  return <VariantCard variant="ai" {...props} />;
}

interface LabelProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  className?: string;
}
export function Badge({ children, className = "", ...props }: LabelProps) {
  return (
    <span className={`ds-badge ${className}`} {...props}>
      {children}
    </span>
  );
}
export function Tag({ children, className = "", ...props }: LabelProps) {
  return (
    <span className={`ds-tag ${className}`} {...props}>
      {children}
    </span>
  );
}
export function Chip({ children, className = "", ...props }: LabelProps) {
  return (
    <span className={`ds-chip ${className}`} {...props}>
      {children}
    </span>
  );
}
