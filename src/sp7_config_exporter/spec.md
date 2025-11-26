# SP7 Config Exporter Spec (v2)

## Responsibility
Export all LLM and storage bindings for a given project+env into a requested format.

## Inputs
- `ResolutionMaps` (from SP5).
- `project`, `env`, `format` (json, yaml, env).

## Outputs
- `ExportedConfig` (structured object) OR plain text for env vars.

## Core Logic
1.  **Gather Configs**: Collect LLM and Store roles for (project, env).
2.  **Format**:
    - **JSON/YAML**: Structured export.
    - **Env**: Flatten keys to `RO_LLM_<ROLE>_<FIELD>` and `RO_STORE_<ROLE>_<FIELD>`.

## Interfaces
```python
def export_config(
    resolution_maps: ResolutionMaps,
    project: str,
    env: str,
    format: str
) -> Union[str, Dict]:
    pass
```
