# SP7 – Scoring Engine

## Purpose

Score and rank filtered candidates using multi-factor weighted scoring.

## Inputs

- **RoleNeed**
- **Weights**
- **List[CanonicalModel]** (filtered)

## Outputs

- **List[Tuple[CanonicalModel, float]]**: Models with scores, sorted descending

## Scoring Dimensions

1. Quality (quality_tier + arena_score)
2. Cost (inverse of cost_tier)
3. Reasoning (reasoning_tier)
4. Creative (creative_tier)
5. Context (context_tokens vs requirement)
6. Freshness (last_updated / release_date)

## Algorithm

For each model:
- Normalize each dimension to [0, 1]
- Apply weights
- Sum to get final score
- Sort descending

## Tie-breaking

1. Provider in allowlist
2. Higher arena_score
3. Higher context_tokens
4. Lexicographic model_id
