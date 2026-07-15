import { memo, useId } from "react";

import { Checkbox, Input, Radio, Select, Textarea } from "../ui";
import { useLocale } from "../../contexts/LocaleContext";
import { assessmentCopy } from "../../i18n/assessment";
import type { AnswerValue, AssessmentQuestion } from "../../types/assessment";

interface AssessmentQuestionFieldProps {
  question: AssessmentQuestion;
  value: AnswerValue | undefined;
  onChange: (value: AnswerValue) => void;
  error?: string;
  disabled?: boolean;
}

function AssessmentQuestionFieldComponent({
  question,
  value,
  onChange,
  error,
  disabled,
}: AssessmentQuestionFieldProps) {
  const { locale } = useLocale();
  const copy = assessmentCopy[locale];
  const groupId = useId();
  const common = {
    id: `${groupId}-answer`,
    label: question.title,
    hint: question.description ?? undefined,
    error,
    disabled,
    required: question.required,
  };

  if (question.type === "textarea") {
    return (
      <Textarea
        {...common}
        rows={5}
        placeholder={question.placeholder ?? undefined}
        value={typeof value === "string" ? value : ""}
        onChange={(event) => onChange(event.target.value)}
      />
    );
  }

  if (["text", "date", "time"].includes(question.type)) {
    return (
      <Input
        {...common}
        type={question.type}
        placeholder={question.placeholder ?? undefined}
        value={typeof value === "string" ? value : ""}
        onChange={(event) => onChange(event.target.value)}
      />
    );
  }

  if (["number", "integer", "height", "weight"].includes(question.type)) {
    return (
      <div className="assessment-number-field">
        <Input
          {...common}
          type="number"
          inputMode={question.type === "integer" ? "numeric" : "decimal"}
          min={question.min ?? undefined}
          max={question.max ?? undefined}
          step={question.type === "integer" ? 1 : "any"}
          value={typeof value === "number" ? value : ""}
          onChange={(event) => {
            const next = event.target.value;
            if (next === "") return onChange("");
            onChange(question.type === "integer" ? Number.parseInt(next, 10) : Number(next));
          }}
        />
        {question.unit ? <span className="assessment-unit">{question.unit}</span> : null}
      </div>
    );
  }

  if (question.type === "boolean") {
    return (
      <fieldset
        className="assessment-choice-field"
        aria-describedby={error ? `${groupId}-error` : undefined}
      >
        <legend>{question.title}</legend>
        {question.description ? <p>{question.description}</p> : null}
        <div className="assessment-choice-grid is-boolean">
          <Radio
            label={copy.yes}
            name={groupId}
            checked={value === true}
            disabled={disabled}
            onChange={() => onChange(true)}
          />
          <Radio
            label={copy.no}
            name={groupId}
            checked={value === false}
            disabled={disabled}
            onChange={() => onChange(false)}
          />
        </div>
        {error ? (
          <p className="ds-field-error" id={`${groupId}-error`} role="alert">
            {error}
          </p>
        ) : null}
      </fieldset>
    );
  }

  if (question.type === "single_choice" && question.options.length > 3) {
    return (
      <Select
        {...common}
        value={typeof value === "string" ? value : ""}
        options={[{ value: "", label: copy.selectOne }, ...question.options]}
        onChange={(event) => onChange(event.target.value)}
      />
    );
  }

  if (question.type === "single_choice") {
    return (
      <fieldset className="assessment-choice-field">
        <legend>{question.title}</legend>
        {question.description ? <p>{question.description}</p> : null}
        <span className="assessment-choice-instruction">{copy.selectOne}</span>
        <div className="assessment-choice-grid">
          {question.options.map((option) => (
            <Radio
              key={option.value}
              label={option.label}
              name={groupId}
              value={option.value}
              checked={value === option.value}
              disabled={disabled}
              onChange={() => onChange(option.value)}
            />
          ))}
        </div>
        {error ? (
          <p className="ds-field-error" role="alert">
            {error}
          </p>
        ) : null}
      </fieldset>
    );
  }

  if (question.type === "multiple_choice") {
    const selected = Array.isArray(value) ? value : [];
    return (
      <fieldset className="assessment-choice-field">
        <legend>{question.title}</legend>
        {question.description ? <p>{question.description}</p> : null}
        <span className="assessment-choice-instruction">{copy.selectMany}</span>
        <div className="assessment-choice-grid">
          {question.options.map((option) => (
            <Checkbox
              key={option.value}
              label={option.label}
              checked={selected.includes(option.value)}
              disabled={disabled}
              onChange={(event) =>
                onChange(
                  event.target.checked
                    ? [...selected, option.value]
                    : selected.filter((item) => item !== option.value),
                )
              }
            />
          ))}
        </div>
        {error ? (
          <p className="ds-field-error" role="alert">
            {error}
          </p>
        ) : null}
      </fieldset>
    );
  }

  const sliderValue = typeof value === "number" ? value : (question.min ?? 0);
  return (
    <div className="assessment-slider-field">
      <label htmlFor={`${groupId}-slider`}>{question.title}</label>
      {question.description ? <p>{question.description}</p> : null}
      <output htmlFor={`${groupId}-slider`}>{sliderValue}</output>
      <input
        id={`${groupId}-slider`}
        type="range"
        min={question.min ?? 0}
        max={question.max ?? 100}
        value={sliderValue}
        disabled={disabled}
        aria-invalid={Boolean(error)}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      <div className="assessment-slider-bounds" aria-hidden="true">
        <span>{question.min ?? 0}</span>
        <span>{question.max ?? 100}</span>
      </div>
      {error ? (
        <p className="ds-field-error" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export const AssessmentQuestionField = memo(AssessmentQuestionFieldComponent);
