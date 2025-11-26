# SP5 Resolution Map Builder Spec (v2)

## Responsibility
Combine project/env role bindings with the ModelCatalog and StorageCatalog to build fast lookup maps.

## Inputs
- `StaticConfig` (from SP1).
- `ModelCatalog` (from SP3).
- `StorageCatalog` (from SP4).

## Outputs
- `ResolutionMaps`:
    - `llm`: `(project, env, role) -> LLMResolution`
    - `store`: `(project, env, role) -> StoreResolution`

## Core Logic
1.  **Iterate Contexts**: Loop through every project and env.
2.  **Resolve LLM Roles**:
    - For each role in `env_config.llm`:
        - Check if provider/model exists in `ModelCatalog`.
        - If yes, `status="ok"`.
        - If no, `status="error"`.
3.  **Resolve Store Roles**:
    - For each role in `env_config.storage`:
        - Check `StorageCatalog`.
        - `status="ok"` or `"error"`.

## Interfaces
```python
def build_resolution_maps(
    static_config: StaticConfig,
    model_catalog: ModelCatalog,
    storage_catalog: StorageCatalog
) -> ResolutionMaps:
    pass
```
