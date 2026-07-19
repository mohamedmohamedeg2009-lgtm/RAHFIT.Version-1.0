import React from "react";
import { useOptionalTheme } from "../../theme/ThemeProvider";

interface RahafitLogoProps {
  variant?: "full" | "icon-only";
  size?: "sm" | "md" | "lg" | "xl" | number;
  themeMode?: "auto" | "dark" | "light";
  className?: string;
}

export const RahafitLogo: React.FC<RahafitLogoProps> = ({
  variant = "full",
  size = "md",
  themeMode = "auto",
  className = "",
}) => {
  const themeCtx = useOptionalTheme();
  const theme = themeCtx?.theme ?? "dark";
  const isDark = themeMode === "auto" ? theme === "dark" : themeMode === "dark";

  // Determine numerical dimension
  const getDimension = () => {
    if (typeof size === "number") return size;
    switch (size) {
      case "sm":
        return 24;
      case "lg":
        return 40;
      case "xl":
        return 48;
      case "md":
      default:
        return 32;
    }
  };

  const dim = getDimension();
  const iconPrimaryColor = isDark ? "#f4c86b" : "#0f766e";
  const iconSecondaryColor = isDark ? "#14b8a6" : "#115e59";
  const textColor = isDark ? "#f4c86b" : "#0f766e";

  return (
    <div
      className={`rahafit-logo-container flex items-center gap-2.5 ${className}`}
      style={{ display: "inline-flex", alignItems: "center" }}
    >
      {/* Rahafit SVG Monogram - Transparent Background */}
      <svg
        width={dim}
        height={dim}
        viewBox="0 0 44 44"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        className="rahafit-logo-icon shrink-0"
      >
        {/* Athletic 'R' & Loop (Transparent Cutout) */}
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M14 11H25C28.866 11 32 14.134 32 18C32 21.866 28.866 25 25 25H20V33H14V11ZM20 16H24.5C25.8807 16 27 17.1193 27 18.5C27 19.8807 25.8807 21 24.5 21H20V16Z"
          fill={iconPrimaryColor}
        />
        {/* Dynamic diagonal stride */}
        <path d="M22 23L31 33H24.5L18 25.5L22 23Z" fill={iconSecondaryColor} />
        {/* Diamond Star Accent */}
        <path
          d="M33 11L34.5 14L37.5 15.5L34.5 17L33 20L31.5 17L28.5 15.5L31.5 14L33 11Z"
          fill={iconPrimaryColor}
        />
      </svg>

      {/* Wordmark (only if variant is 'full') */}
      {variant === "full" && (
        <span
          className="rahafit-logo-text font-extrabold tracking-tight"
          style={{
            color: textColor,
            fontSize: dim >= 40 ? "1.5rem" : dim >= 32 ? "1.25rem" : "1.1rem",
            lineHeight: 1,
            fontWeight: 800,
            letterSpacing: "-0.02em",
          }}
        >
          Rahafit
        </span>
      )}
    </div>
  );
};
