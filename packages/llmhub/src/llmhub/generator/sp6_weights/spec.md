# SP6 – Weights

## Purpose

Derive numeric scoring weights from RoleNeed preferences and characteristics.

## Inputs

- **RoleNeed**: Role with biases and preferences

## Outputs

- **Weights**: Normalized weights for scoring dimensions

## Public Interfaces

```python
class Weights(BaseModel):
    w_quality: float
    w_cost: float
    w_reasoning: float
    w_creative: float
    w_context: float
    w_freshness: float

def derive_weights(role: RoleNeed) -> Weights:
    """Derive scoring weights from role need."""
```

## Algorithm

Weights are derived considering:
- quality_bias, cost_bias, latency_sensitivity
- task_kind, importance
- reasoning_tier_pref, creative_tier_pref

All weights sum to 1.0.

## Invariants

- Weights in [0, 1]
- Sum of all weights = 1.0
- Deterministic (same input → same output)
