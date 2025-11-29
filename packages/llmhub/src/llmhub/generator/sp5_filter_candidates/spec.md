# SP5 – Filter Candidates

## Purpose

Apply hard constraints from a RoleNeed to filter the catalog, returning only models that meet all mandatory requirements.

## Inputs

- **RoleNeed**: Role with constraints
- **List[CanonicalModel]**: Full catalog

## Outputs

- **List[CanonicalModel]**: Filtered candidates

## Public Interfaces

```python
def filter_candidates(
    role: RoleNeed,
    models: list[CanonicalModel]
) -> list[CanonicalModel]:
    """Filter models by hard constraints."""
```

## Constraints Applied

1. Provider allowlist/blocklist
2. Model denylist
3. Required modalities (input/output)
4. Required capabilities (reasoning, tools, structured output)
5. Minimum context window

## Invariants

- Pure function (no side effects)
- No scoring or ranking (just filtering)
- Permissive where possible (missing data doesn't auto-exclude)

## Non-goals

- Scoring or ranking (handled by SP7)
- Relaxation (handled by SP8)
