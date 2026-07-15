# RAHFIT AI Design System

The RAHFIT AI design system is the shared visual and interaction foundation for future screens. It contains no product or business logic. Feature teams should compose the generic UI primitives and tokens instead of inventing screen-specific colours, spacing, focus states, or feedback patterns.

## Theme

`ThemeProvider` owns the user’s light/dark preference and applies `data-theme` to the document root. The first choice respects a stored preference, then the operating-system preference, and finally light mode. `useTheme` exposes the current mode and controlled toggle. Tokens are semantic, so components use `var(--color-primary)` and related names rather than raw hex values. Light and dark themes preserve the same semantic meaning and contrast intent.

## Tokens

Tokens are available as TypeScript constants in `src/tokens` and as CSS custom properties in `src/styles/tokens.css`.

| Group | Contract |
| --- | --- |
| Colour | Primary, secondary, background, surface, card, border, text primary/secondary, success, warning, danger, info, accent, focus ring, and AI brand. |
| Typography | Display, Heading XL/L/M/S, Body Large/Body/Body Small, Caption, and Button. Arabic and Latin text must use a compatible readable font stack. |
| Spacing | 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, and 64 pixel steps represented as rem values. |
| Radius | xs, sm, md, lg, xl, 2xl, and pill. |
| Shadows | Soft and card shadows only; no heavy material-style elevation. |
| Motion | Fast, normal, slow durations and a shared easing curve. Reduced-motion users receive no essential animation. |
| Breakpoints | Mobile, tablet (640px), laptop (1024px), desktop (1280px), and ultra-wide (1536px). |

## Components

Import generic primitives from `src/components/ui`:

- `Button`: primary, secondary, outline, ghost, danger, loading, and disabled states with small/medium/large sizes.
- `Input`, `Textarea`, `PasswordInput`, `SearchInput`, `Select`, `Checkbox`, `Radio`, and `Switch`: labels, hints, errors, and accessible relationships are built into the controls.
- `Card`, `MetricCard`, `ProfileCard`, `WorkoutCard`, `NutritionCard`, and `AICoachCard`: structural surfaces with semantic accent variants, not business content.
- `Badge`, `Tag`, and `Chip`: compact status and categorisation treatments.
- `Alert`: success, warning, danger, and info messaging with semantic status/alert roles.
- `Dialog`, `Modal`, and `Drawer`: dismissible overlays with labelled dialog semantics and Escape handling.
- `LinearProgress`, `CircularProgress`, and `StepProgress`: labelled progress semantics and bounded values.
- `Spinner`, `Skeleton`, and `FullPageLoader`: loading states that do not expose private data.
- `EmptyState` and `ErrorState`: generic, workout, nutrition, assessment, AI, 404, 500, and offline messaging primitives.

These components are intentionally content-light. A feature supplies its own labels, actions, and domain state; the system supplies visual consistency, accessibility structure, and interaction states.

## Accessibility

The baseline is WCAG AA intent: semantic HTML, explicit labels, keyboard operation, visible focus, sufficient contrast, screen-reader status/error announcements, large-text resilience, touch-friendly targets, and reduced-motion support. Colour is never the only status signal. Dialogs have labelled modal semantics and Escape dismissal. Progress controls expose values through ARIA. Arabic RTL and English LTR are supported by logical spacing, direction-neutral primitives, and avoidance of left/right assumptions.

## Responsive and RTL usage

Use CSS logical properties such as `margin-inline`, `padding-inline`, `inset-inline`, and `border-inline` for directional layout. Mobile is the default; tablet and desktop add space and composition rather than requiring a separate feature implementation. Keep content readable at narrow widths, browser zoom, large fonts, and ultra-wide layouts.

## Usage examples

```tsx
<Button variant="primary" loading={saving}>Save changes</Button>
<Input label="Email address" type="email" hint="We will use this to sign you in." />
<Alert variant="warning" title="Review needed">Your current context needs an update.</Alert>
<LinearProgress value={3} max={5} label="Assessment progress" />
```

Examples demonstrate composition only; feature code remains responsible for data, business rules, and API calls outside the design-system layer.

## Best practices

1. Prefer semantic tokens and UI primitives over raw colour, spacing, or border values.
2. Give every interactive control a visible purpose, a keyboard path, and an accessible name.
3. Use one primary action per context and make loading/disabled states explicit.
4. Pair empty, error, offline, and stale states with a useful recovery action where one exists.
5. Keep sensitive or health-related wording outside generic component defaults; domain owners provide safe copy.
6. Test both themes, keyboard operation, reduced motion, narrow screens, and RTL direction before release.
7. Extend a primitive only when the interaction is reusable; do not create feature-specific duplicates.
