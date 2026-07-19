import React from "react";
import type { LucideIcon } from "lucide-react";

interface HeroFloatingCardProps {
  icon: LucideIcon;
  title: string;
  subtitle?: string;
  badge?: string;
  iconColor?: string;
  iconBg?: string;
  className?: string;
  style?: React.CSSProperties;
}

export const HeroFloatingCard: React.FC<HeroFloatingCardProps> = ({
  icon: Icon,
  title,
  subtitle,
  badge,
  iconColor = "var(--color-primary)",
  iconBg = "rgba(20, 184, 166, 0.15)",
  className = "",
  style,
}) => {
  return (
    <div className={`hero-floating-card ${className}`} style={style} aria-hidden="true">
      <div className="hero-floating-card-icon" style={{ backgroundColor: iconBg }}>
        <Icon size={18} color={iconColor} />
      </div>
      <div className="hero-floating-card-content">
        <div className="hero-floating-card-title">{title}</div>
        {subtitle && <div className="hero-floating-card-subtitle">{subtitle}</div>}
      </div>
      {badge && <span className="hero-floating-card-badge">{badge}</span>}
    </div>
  );
};
