# Generator Module Specification

## Purpose

The Generator module is the bridge from **human spec** → **canonical role needs** → **model selection** → **machine config** for LLM Hub Runtime.

It provides a structured, deterministic pipeline for transforming user-written specifications into machine-readable configurations that the runtime can execute.

## Inputs

- **Human Spec YAML**: A user-written `llmhub.spec.yaml` file containing:
  - Project metadata
  - Natural language role descriptions
  - Preferences for quality, cost, latency
  - Provider allowlists/blocklists
  - Other constraints

## Outputs

- **Machine Config YAML**: A runtime-ready `llmhub.yaml` file containing:
  - Concrete provider + model assignments for each role
  - Backup models
  - Configuration parameters
  - Optional metadata (rationale, relaxations applied)

## Architecture

The generator is organized into 10 subproblems (SP1-SP10), each with tight boundaries:

1. **SP1 - Spec Schema**: Parse and validate human spec YAML
2. **SP2 - Needs Interpreter**: Use LLM to convert spec to canonical RoleNeeds
3. **SP3 - Needs Schema**: Define RoleNeed data model
4. **SP4 - Catalog View**: Load catalog as CanonicalModel list
5. **SP5 - Filter Candidates**: Apply hard constraints
6. **SP6 - Weights**: Derive scoring weights from role preferences
7. **SP7 - Scoring Engine**: Score and rank filtered candidates
8. **SP8 - Relaxation Engine**: Systematically relax constraints if no matches
9. **SP9 - Selector Orchestrator**: Coordinate selection for one role
10. **SP10 - Machine Config Emitter**: Assemble final machine config

## Flow

```
Human Spec YAML
  ↓ [SP1: parse & validate]
ProjectSpec
  ↓ [SP2: LLM interpretation]
List[RoleNeed]
  ↓ [SP4: load catalog]
  ↓ [for each role:]
  ↓   [SP5: filter] → [SP6: weights] → [SP7: score] → [SP9: select]
  ↓   (or SP8: relaxation if needed)
List[SelectionResult]
  ↓ [SP10: emit machine config]
Machine Config YAML
```

## Invariants

- **No network calls**: All data comes from LLM Hub Runtime or Catalog module
- **Deterministic**: Same spec + catalog → same machine config
- **Pure functions**: No side effects except file I/O in SP1 and SP10
- **Forward compatible**: New fields must not break existing code

## Non-goals

- Real-time model discovery (handled by Catalog)
- Live API calls to providers (handled by Runtime)
- UI/visualization (separate concern)
- Model performance benchmarking (use Arena data)

## Public API

Main entrypoint:

```python
from llmhub.generator import generate_machine_config
from llmhub_runtime import LLMHub

hub = LLMHub(config_path="llmhub.yaml")
machine_config = generate_machine_config(
    spec_path="llmhub.spec.yaml",
    hub=hub,
    catalog_override=None  # optional for testing
)
```

## Testing Strategy

- Unit tests for each subproblem (SP1-SP10)
- End-to-end test with mock catalog and LLM
- Validation that output works with Runtime
