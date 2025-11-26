# SP6 Runtime Resolver Service Spec (v2)

## Responsibility
Implement the runtime APIs (`resolve_llm`, `resolve_store`) using the pre-computed ResolutionMaps.

## Inputs
- `ResolutionMaps` (from SP5).
- `project`, `env`, `role`.

## Outputs
- `LLMResolution` or `StoreResolution`.

## Core Logic
1.  **Resolve LLM**:
    - Lookup `(project, env, role)` in `ResolutionMaps.llm`.
    - Handle fallbacks if provided in options (optional).
2.  **Resolve Store**:
    - Lookup in `ResolutionMaps.store`.

## Interfaces
```python
class RuntimeResolver:
    def resolve_llm(self, project: str, env: str, role: str) -> LLMResolution:
        pass

    def resolve_store(self, project: str, env: str, role: str) -> StoreResolution:
        pass
```
