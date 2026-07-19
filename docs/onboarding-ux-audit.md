# Onboarding and assessment UX audit

## Inventory (before)

The Version 1 assessment has 31 questions. A standard path can require 22+ answers:

| Area | Questions | Decision |
| --- | --- | --- |
| Body | age, height, current weight | Keep: used by initial training/nutrition calculations. |
| Goal | primary goal, target weight | Keep goal; postpone target weight to nutrition/progress. |
| Injury and safety | injury, affected area, knee details, serious injury, pregnancy, seven red-flag prompts | Keep injury and safety declaration; make details conditional; merge the generic safety declaration into one clear prompt. |
| Training setup | experience, home training, home/gym equipment | Keep: required for safe first workout generation. |
| Lifestyle | sleep, stress | Postpone to daily check-in, where they are measured for that day. |
| Nutrition | eating pattern | Postpone to nutrition setup; it is not needed to start training. |
| Advanced/sport | advanced programming, sports, football position, goalkeeper focus | Postpone to feature-specific sport programming. |
| Profile overlap | gender and male-specific context | Postpone unless a relevant feature needs it; it is not used by the initial plan. |

## Version 2 essential setup

Version 2 has 13 catalog questions; a typical no-injury path presents 10 questions because equipment is conditional. It retains all initial-plan inputs and safety gates:

1. Body basics: age, height, weight
2. Goal and training experience
3. Training setting and matching equipment
4. Current injury and only relevant follow-up
5. Pregnancy relevance and one plain-language safety declaration

Existing Version 1 sessions remain resumable. New sessions use Version 2 automatically.

## Progressive profiling map

- Daily check-in: sleep, stress, energy, soreness, pain, hydration.
- Nutrition: target weight and eating pattern.
- Advanced/sport plans: programming style, sport, position, goalkeeper focus.
- Relevant health workflows: gender-specific context.

## Remaining follow-up work

- Add explicit progressive-profile entry points to nutrition and sport workflows.
- Consolidate the seven legacy red-flag prompts for Version 1 migrations only after clinical review.
- Replace remaining legacy dashboard tests that mock the retired dashboard contract.
