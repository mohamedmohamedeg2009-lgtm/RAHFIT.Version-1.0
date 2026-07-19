import { useEffect, useRef } from "react";

export interface FormErrorSummaryProps {
  errors: Array<{ field: string; message: string }>;
  title?: string;
}

export function FormErrorSummary({ errors, title = "Please correct the following" }: FormErrorSummaryProps) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (errors.length) ref.current?.focus();
  }, [errors.length]);
  if (!errors.length) return null;
  return (
    <div className="form-alert" ref={ref} role="alert" tabIndex={-1}>
      <p>{title}</p>
      <ul>
        {errors.map(({ field, message }) => (
          <li key={field}>
            <a href={`#${field}`}>{message}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
