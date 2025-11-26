# SP1 Config Loader Spec (v2)

## Responsibility
Load YAML config files into typed Pydantic models, matching the v2 schema.

## Inputs
- `config/providers.yaml`: Provider definitions with `auth_profile`, `api_base`, `adapter`.
- `config/projects.yaml`: Project definitions with nested `llm` and `storage` blocks.
- `config/roles.yaml`: Role definitions.

## Outputs
- `StaticConfig`: A data structure containing:
    - `providers`: List of `ProviderConfig`
    - `projects`: List of `ProjectConfig`
    - `roles`: `RoleRegistry`

## Core Logic
1.  **Load Files**: Read `providers.yaml`, `projects.yaml`, and `roles.yaml`.
2.  **Validate Schema**:
    - `ProviderConfig`: `name`, `kind`, `auth_profile`, `api_base`, `adapter`.
    - `ProjectConfig`: `name`, `envs` (dict of `EnvConfig`).
    - `EnvConfig`: `llm` (dict of `LLMRoleBinding`), `storage` (dict of `StoreRoleBinding`).
3.  **Construct Objects**: Build the `StaticConfig` object.

## Interfaces
```python
def load_static_config(config_dir: str) -> StaticConfig:
    """
    Reads and validates configuration from the specified directory.
    """
    pass
```
