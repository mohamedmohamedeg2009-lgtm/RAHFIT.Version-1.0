interface FormAlertProps {
  message: string | null;
}

export function FormAlert({ message }: FormAlertProps) {
  if (!message) return null;
  return (
    <div className="form-alert" role="alert" tabIndex={-1}>
      {message}
    </div>
  );
}
