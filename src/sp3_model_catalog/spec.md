# SP3 Provider Model Discovery & Catalog Spec (v2)

## Responsibility
Normalize provider model metadata using provider-specific adapters.

## Inputs
- `ProviderConfigs` (from SP1).
- `AuthRegistry` (from SP2).

## Outputs
- `ModelCatalog`: A collection of `ProviderModel` records.

## Core Logic
1.  **Initialize Adapters**: Instantiate adapters based on `adapter` field in config.
    - Supported: `openai_adapter`, `gemini_adapter`, `anthropic_adapter`, `deepseek_adapter`, `qwen_adapter`.
2.  **Fetch Models**:
    - Call `adapter.list_models(auth_key, api_base)`.
3.  **Normalize**: Adapter returns normalized `ProviderModel` objects.
4.  **Catalog**: aggregate all models.

## Interfaces
```python
class ProviderAdapter:
    def list_models(self, auth_key: str, api_base: str) -> List[ProviderModel]:
        pass

def build_model_catalog(static_config: StaticConfig, auth_registry: AuthRegistry) -> ModelCatalog:
    pass
```
