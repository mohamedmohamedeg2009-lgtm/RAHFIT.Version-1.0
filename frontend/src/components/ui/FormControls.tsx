import {
  forwardRef,
  useId,
  useState,
  type InputHTMLAttributes,
  type TextareaHTMLAttributes,
} from "react";

interface FieldProps {
  label?: string;
  hint?: string;
  error?: string;
  id?: string;
}
type InputProps = FieldProps & InputHTMLAttributes<HTMLInputElement>;

function FieldMessage({ id, hint, error }: Pick<FieldProps, "id" | "hint" | "error">) {
  return error ? (
    <p className="ds-field-error" id={`${id}-error`}>
      {error}
    </p>
  ) : hint ? (
    <p className="ds-field-hint" id={`${id}-hint`}>
      {hint}
    </p>
  ) : null;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, hint, error, id: providedId, className = "", ...props },
  ref,
) {
  const generatedId = useId();
  const id = providedId ?? generatedId;
  return (
    <div className="ds-field">
      <label htmlFor={id}>
        {label}
        {props.required ? <span aria-hidden="true"> *</span> : null}
      </label>
      <input
        ref={ref}
        id={id}
        className={`ds-input ${className}`}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        {...props}
      />
      <FieldMessage id={id} hint={hint} error={error} />
    </div>
  );
});

type TextareaProps = FieldProps & TextareaHTMLAttributes<HTMLTextAreaElement>;
export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { label, hint, error, id: providedId, className = "", ...props },
  ref,
) {
  const generatedId = useId();
  const id = providedId ?? generatedId;
  return (
    <div className="ds-field">
      <label htmlFor={id}>{label}</label>
      <textarea
        ref={ref}
        id={id}
        className={`ds-input ds-textarea ${className}`}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        {...props}
      />
      <FieldMessage id={id} hint={hint} error={error} />
    </div>
  );
});

export function PasswordInput(props: Omit<InputProps, "type">) {
  const [visible, setVisible] = useState(false);
  return (
    <div className="ds-password">
      <Input {...props} type={visible ? "text" : "password"} />
      <button
        type="button"
        className="ds-password-toggle"
        onClick={() => setVisible((current) => !current)}
        aria-pressed={visible}
        aria-label={visible ? "Hide password" : "Show password"}
      >
        {visible ? "Hide" : "Show"}
      </button>
    </div>
  );
}

export function SearchInput(props: Omit<InputProps, "type">) {
  return <Input {...props} type="search" />;
}

interface SelectProps extends FieldProps, React.SelectHTMLAttributes<HTMLSelectElement> {
  options: Array<{ label: string; value: string }>;
}
export function Select({
  label,
  hint,
  error,
  id: providedId,
  options,
  className = "",
  ...props
}: SelectProps) {
  const generatedId = useId();
  const id = providedId ?? generatedId;
  return (
    <div className="ds-field">
      <label htmlFor={id}>{label}</label>
      <select
        id={id}
        className={`ds-input ds-select ${className}`}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        {...props}
      >
        {options.map((option) => (
          <option value={option.value} key={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <FieldMessage id={id} hint={hint} error={error} />
    </div>
  );
}

interface ChoiceProps {
  label: string;
  description?: string;
  error?: string;
}
export function Checkbox({
  label,
  description,
  error,
  ...props
}: ChoiceProps & Omit<InputHTMLAttributes<HTMLInputElement>, "type">) {
  const generatedId = useId();
  const id = props.id ?? generatedId;
  const errorId = `${id}-error`;
  return (
    <label className="ds-choice" htmlFor={id}>
      <input id={id} type="checkbox" aria-invalid={Boolean(error)} aria-describedby={error ? errorId : undefined} {...props} />
      <span>
        <strong>{label}</strong>
        {description ? <small>{description}</small> : null}
      </span>
      {error ? <em id={errorId}>{error}</em> : null}
    </label>
  );
}
export function Radio({
  label,
  description,
  error,
  ...props
}: ChoiceProps & Omit<InputHTMLAttributes<HTMLInputElement>, "type">) {
  const generatedId = useId();
  const id = props.id ?? generatedId;
  const errorId = `${id}-error`;
  return (
    <label className="ds-choice" htmlFor={id}>
      <input id={id} type="radio" aria-invalid={Boolean(error)} aria-describedby={error ? errorId : undefined} {...props} />
      <span>
        <strong>{label}</strong>
        {description ? <small>{description}</small> : null}
      </span>
      {error ? <em id={errorId}>{error}</em> : null}
    </label>
  );
}
export function Switch({
  label,
  description,
  ...props
}: ChoiceProps & Omit<InputHTMLAttributes<HTMLInputElement>, "type">) {
  return (
    <label className="ds-switch">
      <input type="checkbox" role="switch" {...props} />
      <span className="ds-switch-track" aria-hidden="true" />
      <span>
        <strong>{label}</strong>
        {description ? <small>{description}</small> : null}
      </span>
    </label>
  );
}
