# SP2 – Needs Interpreter

## Purpose

Convert ProjectSpec into canonical RoleNeed objects using an LLM with structured JSON output.

## Inputs

- **ProjectSpec** from SP1
- **LLMHub** instance (or injectable llm_call function)
- Model role name (e.g., "llm.generator")

## Outputs

- **List[RoleNeed]**: Canonical role needs (raw JSON from LLM)

## Public Interfaces

```python
def interpret_needs(
    spec: ProjectSpec,
    hub: LLMHub,
    model_role: str = "llm.generator"
) -> List[RoleNeed]:
    """
    Interpret human spec into canonical RoleNeeds using LLM.
    
    Uses structured output to get JSON matching RoleNeed schema.
    """
```

## Invariants

- Exactly one LLM call per project
- Uses structured JSON output
- No catalog access (only interprets spec)

## Non-goals

- Model selection (handled downstream)
- Validation beyond schema (trust LLM output)
