export const colors = {
  light: {
    primary: "#1f6875",
    secondary: "#315a72",
    background: "#f4f7f9",
    surface: "#ffffff",
    card: "#ffffff",
    border: "#dce4e8",
    textPrimary: "#17202f",
    textSecondary: "#687984",
    success: "#28745a",
    warning: "#9b6a1f",
    danger: "#a33d3d",
    info: "#315a72",
    accent: "#f0b94d",
    focusRing: "#f0b94d",
    ai: "#7356a8",
  },
  dark: {
    primary: "#76c5c9",
    secondary: "#9cc8df",
    background: "#0f1c25",
    surface: "#172a36",
    card: "#1b3340",
    border: "#365260",
    textPrimary: "#e6eef2",
    textSecondary: "#b3c5cc",
    success: "#7dd3aa",
    warning: "#f1c477",
    danger: "#f1a4a4",
    info: "#9cc8df",
    accent: "#f4c86b",
    focusRing: "#f4c86b",
    ai: "#c5a8f2",
  },
} as const;

export const spacing = {
  2: "0.125rem",
  4: "0.25rem",
  8: "0.5rem",
  12: "0.75rem",
  16: "1rem",
  20: "1.25rem",
  24: "1.5rem",
  32: "2rem",
  40: "2.5rem",
  48: "3rem",
  64: "4rem",
} as const;

export const radius = {
  xs: "0.25rem",
  sm: "0.375rem",
  md: "0.625rem",
  lg: "0.875rem",
  xl: "1.25rem",
  "2xl": "1.5rem",
  pill: "999px",
} as const;

export const shadows = {
  soft: "0 8px 24px rgba(18, 43, 63, 0.08)",
  card: "0 16px 40px rgba(18, 43, 63, 0.1)",
  focus: "0 0 0 3px color-mix(in srgb, var(--color-focus-ring) 24%, transparent)",
} as const;

export const breakpoints = {
  mobile: "0px",
  tablet: "640px",
  laptop: "1024px",
  desktop: "1280px",
  ultraWide: "1536px",
} as const;

export const motion = {
  fast: "120ms",
  normal: "180ms",
  slow: "280ms",
  easing: "cubic-bezier(0.2, 0.8, 0.2, 1)",
} as const;

export const typography = {
  display: "clamp(2.5rem, 6vw, 5rem)",
  headingXl: "clamp(2rem, 4vw, 3.5rem)",
  headingL: "clamp(1.75rem, 3vw, 2.5rem)",
  headingM: "1.75rem",
  headingS: "1.25rem",
  bodyLarge: "1.125rem",
  body: "1rem",
  bodySmall: "0.875rem",
  caption: "0.75rem",
  button: "0.9375rem",
} as const;
