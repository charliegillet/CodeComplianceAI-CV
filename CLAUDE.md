# CLAUDE.md

## Project Overview
This repository contains a Python pipeline for processing architectural floor plans.
The system extracts spatial features (doors, elevators, hallways, ramps) and stores
structured outputs for compliance analysis.

## Tech Stack
- Python
- OpenCV
- PyTorch
- Label Studio
- PostgreSQL

## Design Principles
- Keep pipelines modular and testable
- Avoid unnecessary dependencies
- Prefer deterministic processing over heuristics when possible
- Write clear, readable code rather than clever abstractions

## Coding Standards
- Python 3.11+
- Use type hints
- Use pathlib instead of os paths
- Prefer dataclasses for structured objects
- Keep functions under ~50 lines

## Testing
- Use pytest
- Add tests for any new logic added to the pipeline

## When Modifying Code
- Do not rewrite large modules unless necessary
- Prefer minimal diffs
- Maintain existing architecture
- Ask before introducing new libraries
