# SP9 – Selector Orchestrator

## Purpose

Single entrypoint to select model(s) for a RoleNeed, coordinating filter, scoring, and relaxation.

## Inputs

- **RoleNeed**
- **List[CanonicalModel]**
- **SelectorOptions** (optional)

## Outputs

- **SelectionResult**: Primary model, backups, rationale, relaxations

##  Algorithm

1. SP6: Derive weights
2. SP5: Filter candidates
3. If empty → SP8: Relax and select
4. Else → SP7: Score and rank
5. Pick primary (top 1) and backups (next N)
6. Generate rationale
7. Return SelectionResult
