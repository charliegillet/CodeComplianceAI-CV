# Code Capture AI — Annotation Guide v1

Annotate these 17 elements on Architecttura floor plans in Label Studio using bounding boxes.

---

## Symbol Key

[INSERT: Architecttura symbol key image]

## Fully Annotated Examples

[INSERT: 1-2 screenshots of a fully labeled floor plan in Label Studio showing multiple classes annotated]

---

## Rules

- **Tight boxes** — minimal whitespace around each element
- **Separate overlapping elements** — a door and its door tag get separate boxes
- **Unsure? Skip it** — a wrong label is worse than a missing one. Ask in Slack with a screenshot

---

## Classes

### Building Elements

| Example | Class | Box guidance |
|---------|-------|-------------|
| [INSERT] | **Door** | Include swing arc, not the door tag |
| [INSERT] | **Stairs** | Full staircase including treads and direction arrow |
| [INSERT] | **Ramp** | Full ramp run, landing to landing |
| [INSERT] | **Elevator** | Full shaft/car outline |
| [INSERT] | **Corridor** | Wall to wall, full length |

### Plumbing Fixtures

| Example | Class | Box guidance |
|---------|-------|-------------|
| [INSERT] | **Toilet** | Fixture only, not grab bars |
| [INSERT] | **Sink** | Fixture only |
| [INSERT] | **Shower** | Full enclosure outline |
| [INSERT] | **Bathtub** | Tub outline |
| [INSERT] | **Urinal** | Fixture only |
| [INSERT] | **Drinking Fountain** | Each fountain individually, even if paired |

### Other Elements

| Example | Class | Box guidance |
|---------|-------|-------------|
| [INSERT] | **Handrail** | Full run along stair/ramp |
| [INSERT] | **Counter** | Full counter including any lowered section |

### Annotations & Symbols

| Example | Class | Box guidance |
|---------|-------|-------------|
| [INSERT] | **Dimension Line** | Arrows + extension lines + measurement text |
| [INSERT] | **Room Tag** | Room name + number together in one box |
| [INSERT] | **Door Tag** | Tag symbol + text only, not the door |
| [INSERT] | **Slope Arrow** | Arrow + slope text |

---

## Edge Cases

- **Door without a swing arc** (sliding/pocket) — still annotate as door
- **Grab bars** — skip for v1
- **Elements not on this list** — skip for v1
- **Disagreement between annotators** — flag in Slack, we'll align
