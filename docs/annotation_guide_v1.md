# Code Capture AI — Annotation Guide v1

Annotate these 17 elements on Architecttura floor plans in Label Studio using bounding boxes.

---

## Symbol Key

[INSERT: Architecttura symbol key image]

## Fully Annotated Examples

[INSERT: 1-2 screenshots of a fully labeled floor plan in Label Studio showing all classes annotated]

---

## Rules

- **Only annotate floor plans (overhead view).** DO NOT annotate elevations, sections, or details. If the sheet title says "elevations", "sections", or "details", skip it.
- **Tight boxes** — minimal whitespace around each element
- **Separate overlapping elements** — a door and its door tag get separate boxes
- **Unsure? Skip it** — a wrong label is worse than a missing one. Ask in Slack with a screenshot

---

## Classes

### Building Elements

**1. Door** — include swing arc, not the door tag
[INSERT SCREENSHOT]

**2. Stairs** — full staircase including treads and direction arrow
[INSERT SCREENSHOT]

**3. Ramp** — full ramp run, landing to landing
[INSERT SCREENSHOT]

**4. Elevator** — full shaft/car outline
[INSERT SCREENSHOT]

**5. Corridor** — wall to wall, full length
[INSERT SCREENSHOT]

### Fixtures

**6. Toilet** — fixture only, not grab bars
[INSERT SCREENSHOT]

**7. Sink** — fixture only
[INSERT SCREENSHOT]

**8. Shower** — full enclosure outline
[INSERT SCREENSHOT]

**9. Bathtub** — tub outline
[INSERT SCREENSHOT]

**10. Urinal** — fixture only
[INSERT SCREENSHOT]

**11. Drinking Fountain** — each fountain individually, even if paired
[INSERT SCREENSHOT]

### Other Elements

**12. Handrail** — full run along stair/ramp
[INSERT SCREENSHOT]

**13. Counter** — full counter including any lowered section
[INSERT SCREENSHOT]

### Annotations & Symbols

**14. Dimension Line** — arrows + extension lines + measurement text
[INSERT SCREENSHOT]

**15. Room Tag** — room name + number together in one box
[INSERT SCREENSHOT]

**16. Door Tag** — tag symbol + text only, not the door
[INSERT SCREENSHOT]

**17. Slope Arrow** — arrow + slope text
[INSERT SCREENSHOT]

---

## Edge Cases

- **Door without a swing arc** (sliding/pocket) — still annotate as door
- **Grab bars** — skip for v1
- **Elements not on this list** — skip for v1
- **Disagreement between annotators** — flag in Slack, we'll align
