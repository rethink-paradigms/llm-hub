# SP8 – Relaxation Engine

## Purpose

Systematically relax constraints when filtering returns zero candidates.

## Inputs

- **RoleNeed**
- **List[CanonicalModel]** (full catalog)
- **Weights**
- References to SP5 and SP7

## Outputs

- **Tuple[List[Tuple[CanonicalModel, float]], List[str]]**
  - Ranked candidates after relaxation
  - List of applied relaxation steps

## Relaxation Steps (in order)

1. Remove provider_allowlist (keep blocklist)
2. Lower context_min by 25%
3. Turn structured_output_required into preference
4. Turn reasoning_required into preference
5. Turn tools_required into preference

## Algorithm

- Try each relaxation step in sequence
- After each step, re-run filter + scoring
- Return first non-empty result
- Record all applied relaxations
