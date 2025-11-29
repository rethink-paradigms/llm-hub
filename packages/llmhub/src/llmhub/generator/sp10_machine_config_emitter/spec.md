# SP10 – Machine Config Emitter

## Purpose

Assemble all selection results into a machine-readable `llmhub.yaml` config file for LLM Hub Runtime.

## Inputs

- **ProjectSpec**: Original spec metadata
- **List[SelectionResult]**: Selections for all roles

## Outputs

- **MachineConfig**: Python model
- YAML file on disk

## Public Interfaces

```python
def build_machine_config(
    spec: ProjectSpec,
    selections: List[SelectionResult]
) -> MachineConfig:
    """Build MachineConfig from selections."""

def write_machine_config(
    path: str,
    config: MachineConfig
) -> None:
    """Write MachineConfig to YAML file."""
```

## Format

Output format matches LLM Hub Runtime's RuntimeConfig:
- project, env
- providers (with env_key)
- roles (provider, model, mode, params)
- Optional meta section with rationale and relaxations
