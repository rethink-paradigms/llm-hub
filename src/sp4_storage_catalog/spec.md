# SP4 Storage Adapter Registry & Catalog Spec (v2)

## Responsibility
Normalize all configured storage backends into a unified catalog.

## Inputs
- `ProjectConfig` (from SP1): Specifically `envs[env].storage`.

## Outputs
- `StorageCatalog`: A mapping of `{project, env, role} -> StoreConfig`.

## Core Logic
1.  **Iterate Bindings**: Go through each project and environment's storage role bindings.
2.  **Validate**:
    - Check `kind` (vector, sql, blob).
    - Check `backend` (pgvector, sqlite, etc.).
3.  **Register**: Create a `StoreConfig` record.
4.  **Catalog**: Store in `StorageCatalog`.

## Interfaces
```python
def build_storage_catalog(static_config: StaticConfig) -> StorageCatalog:
    pass
```
