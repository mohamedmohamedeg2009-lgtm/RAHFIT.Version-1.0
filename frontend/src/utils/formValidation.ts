export type FieldErrors<T extends string> = Partial<Record<T, string>>;

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/u;

export function normalizeEmail(value: string): string {
  return value.trim().toLowerCase();
}

export function validateEmail(value: string): string | undefined {
  if (!value.trim()) return "Enter your email address.";
  if (value.trim().length > 254 || !emailPattern.test(value.trim())) {
    return "Enter a valid email address.";
  }
  return undefined;
}

export function validatePasswordForLogin(value: string): string | undefined {
  return value ? undefined : "Enter your password.";
}

export function validatePasswordForRegistration(value: string): string | undefined {
  if (!value) return "Create a password.";
  if (value.length < 12 || value.length > 128) {
    return "Use 12 to 128 characters.";
  }
  return undefined;
}

export function validateRequiredText(
  value: string,
  label: string,
  options: { min?: number; max?: number } = {},
): string | undefined {
  const normalized = value.trim();
  if (!normalized) return `${label} is required.`;
  if (options.min && normalized.length < options.min) {
    return `${label} must be at least ${options.min} characters.`;
  }
  if (options.max && normalized.length > options.max) {
    return `${label} must be ${options.max} characters or fewer.`;
  }
  return undefined;
}

export function validateNumber(
  value: number | string,
  label: string,
  min: number,
  max: number,
  required = true,
): string | undefined {
  if (value === "" && !required) return undefined;
  const number = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(number)) return `${label} must be a number.`;
  if (number < min || number > max) return `${label} must be between ${min} and ${max}.`;
  return undefined;
}

export function isValidPastOrTodayDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/u.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value && value <= new Date().toISOString().slice(0, 10);
}

export function isAllowedValue<T extends string>(value: string, values: readonly T[]): value is T {
  return (values as readonly string[]).includes(value);
}
