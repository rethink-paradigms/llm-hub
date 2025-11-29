# SP3 – Needs Schema

## Purpose

Define the canonical **RoleNeed** model used throughout the selector pipeline. This model represents the interpreted needs of a role after LLM processing, with all fields normalized and ready for filtering/scoring.

## Inputs

- **Raw dicts from SP2**: JSON output from LLM interpretation
  ```python
  {
      "id": "analyst",
      "task_kind": "reasoning",
      "importance": "high",
      "quality_bias": 0.8,
      "cost_bias": 0.3,
      ...
  }
  ```

## Outputs

- **List[RoleNeed]**: Validated Pydantic models with all fields normalized

## Public Interfaces

```python
def parse_role_needs(raw: list[dict]) -> list[RoleNeed]:
    """
    Parse raw dicts into validated RoleNeed objects.
    
    Args:
        raw: List of dicts from LLM output
        
    Returns:
        List of validated RoleNeed instances
        
    Raises:
        NeedsSchemaError: If validation fails
    """

class RoleNeed(BaseModel):
    """Canonical role need with all selection criteria."""
    # Identity
    id: str
    
    # Task characteristics
    task_kind: str  # "reasoning", "creative", "factual", etc.
    importance: str  # "low", "medium", "high", "critical"
    
    # Selection weights (0.0-1.0)
    quality_bias: float = 0.5
    cost_bias: float = 0.5
    latency_sensitivity: float = 0.5
    
    # Capabilities (hard constraints)
    reasoning_required: bool = False
    tools_required: bool = False
    structured_output_required: bool = False
    
    # Context requirements
    context_min: Optional[int] = None
    
    # Modalities
    modalities_in: list[str] = ["text"]
    modalities_out: list[str] = ["text"]
    
    # Provider constraints
    provider_allowlist: Optional[list[str]] = None
    provider_blocklist: Optional[list[str]] = None
    model_denylist: Optional[list[str]] = None
    
    # Tier preferences (1-5)
    reasoning_tier_pref: Optional[int] = None
    creative_tier_pref: Optional[int] = None
    
    # Additional context
    notes: Optional[str] = None
```

## Invariants / Constraints

- **Forward compatible**: New fields can be added without breaking old code
- **Sensible defaults**: All optional fields have reasonable defaults
- **Normalized ranges**: Bias values in [0.0, 1.0], tiers in [1, 5]
- **Validation**: Constraints are validated at parsing time

## Non-goals

- Semantic interpretation (handled by SP2)
- Catalog lookups (handled by SP4)
- Scoring logic (handled by SP7)

## Implementation Notes

- Use Pydantic for validation and type safety
- Provide clear field documentation
- Support partial specifications (LLM may not fill all fields)
