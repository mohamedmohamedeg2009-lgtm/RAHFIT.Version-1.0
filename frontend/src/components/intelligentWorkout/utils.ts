export const label = (value: string) =>
  value.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase());

export const formatDate = (value: string) =>
  new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
