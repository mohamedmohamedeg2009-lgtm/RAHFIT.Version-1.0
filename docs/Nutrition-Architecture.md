# RAHFIT AI Nutrition Architecture

## Scope and Pipeline

Sprint 3.5 provides deterministic nutrition targets, safe meal plans, meal logging, hydration tracking, history, and dashboard availability. Python reads the owner-scoped assessment and workout, calculates BMR with Mifflin–St Jeor, applies a fixed activity factor for TDEE, and then a fixed goal factor. Protein uses 1.6–2.0 g/kg, fat 0.8 g/kg, carbohydrate receives remaining energy, fiber uses 14 g/1,000 kcal, and hydration uses 35 mL/kg plus averaged training allowance.

## Food Catalog and Meals

The versioned realistic catalog records serving nutrition, diet tags, halal/vegetarian/vegan status, allergens, glycemic category, meal suitability, active state, and version. Calories are distributed across breakfast, lunch, dinner, and snacks. Foods are filtered then sorted deterministically by diet relevance, protein density, and stable identifier; portions scale to targets.

## Safety

Allergens, vegan/vegetarian, halal, no-pork, and no-seafood constraints are enforced before selection. Assessment `STOP` blocks generation, and insufficient safe foods fail generation. Output is general fitness guidance, not medical nutrition therapy.

## Persistence and API

One active owner-scoped plan is retained while prior plans are archived. Daily progress uses a unique user/date record; meal logging is idempotent and water logging additive. APIs expose current plan, generation, history, meal logging, water intake, and daily summary. Dashboard state uses the same source.

## Future AI and Boundaries

Future AI may explain plans but deterministic equations, safety, and validation remain authoritative. Micronutrients, clinical diet therapy, branded foods, recipes, barcodes, regional administration, and adaptive long-term expenditure are deferred.
