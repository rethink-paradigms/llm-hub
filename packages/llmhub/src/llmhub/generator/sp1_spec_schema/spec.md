# SP1 – Spec Schema

## Purpose

Define and validate the **human spec YAML** structure. This subproblem is responsible for taking raw YAML input (as a Python dict) and transforming it into a strongly-typed, validated `ProjectSpec` model.

## Inputs

- **Raw YAML dict**: Dictionary loaded from user's `llmhub.spec.yaml` file
  ```python
  {
      "project": "my-app",
      "env": "production",
      "roles": {
          "analyst": {
              "kind": "chat",
              "description": "...",
              ...
          }
      }
  }
  ```

## Outputs

- **ProjectSpec**: Validated Pydantic model containing:
  - Project metadata (name, env)
  - Providers configuration
  - Dictionary of role specifications
  - Default preferences

## Public Interfaces

```python
def parse_project_spec(raw: dict) -> ProjectSpec:
    """
    Parse and validate raw YAML dict into ProjectSpec.
    
    Args:
        raw: Dictionary loaded from YAML file
        
    Returns:
        Validated ProjectSpec instance
        
    Raises:
        SpecSchemaError: If validation fails
    """
    
def load_project_spec(path: str) -> ProjectSpec:
    """
    Load ProjectSpec from file path.
    
    Args:
        path: Path to llmhub.spec.yaml
        
    Returns:
        Validated ProjectSpec instance
        
    Raises:
        SpecSchemaError: If file not found or validation fails
    """
```

## Data Models

```python
class ProjectSpec(BaseModel):
    """Complete project specification."""
    project: str
    env: str
    providers: Optional[dict[str, ProviderSpec]] = None
    roles: dict[str, RoleSpec]
    defaults: Optional[DefaultPreferences] = None

class RoleSpec(BaseModel):
    """Specification for a single role."""
    kind: str  # "chat", "embedding", etc.
    description: str
    preferences: Optional[Preferences] = None
    force_provider: Optional[str] = None
    force_model: Optional[str] = None

class Preferences(BaseModel):
    """Role preferences for model selection."""
    latency: Optional[str] = None  # "low", "medium", "high"
    cost: Optional[str] = None
    quality: Optional[str] = None
    providers: Optional[list[str]] = None
```

## Invariants / Constraints

- **No LLM usage**: Pure parsing and validation
- **Provide defaults**: Missing optional fields get sensible defaults
- **Clear errors**: Validation failures produce actionable error messages
- **Forward compatible**: Unknown fields are ignored (not rejected)

## Non-goals

- Semantic validation (e.g., checking if role description makes sense)
- Provider/model existence checks (handled downstream)
- LLM interpretation (handled by SP2)

## Implementation Notes

- Use Pydantic for validation and type safety
- Support both strict and permissive parsing modes
- Provide helpful error messages with field paths
