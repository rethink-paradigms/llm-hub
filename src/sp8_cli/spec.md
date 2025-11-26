# SP8 CLI / API Frontend Spec (v2)

## Responsibility
Expose the runtime resolver and config exporter via CLI.

## Inputs
- `ResolutionMaps`, `ModelCatalog`, `StorageCatalog`.
- User commands.

## Outputs
- Human-readable text/JSON.

## Core Logic
1.  **Initialize System**: Load config, build catalogs/maps.
2.  **Commands**:
    - `resolve-llm <project> <env> <role>`
    - `resolve-store <project> <env> <role>`
    - `export-config --project <p> --env <e> --format <f>`

## Interfaces
```python
def main():
    pass
```
