# SP2 Secrets & Auth Registry Spec (v2)

## Responsibility
Resolve API keys from environment variables based on `auth_profile` defined in provider configs.

## Inputs
- `ProviderConfigs` (from SP1).
- Environment Variables.

## Outputs
- `AuthRegistry`: A mapping of `auth_profile` name -> `api_key`.

## Core Logic
1.  **Iterate Providers**: Go through each provider in `StaticConfig`.
2.  **Resolve Secrets**:
    - For each provider, get `auth_profile`.
    - Construct env var name: `RO_AUTH_<AUTH_PROFILE>_API_KEY`.
    - Look up value in `os.environ`.
    - If missing, raise explicit error.
3.  **Build Map**: Create `AuthRegistry` mapping profile -> key.

## Interfaces
```python
def build_auth_registry(static_config: StaticConfig) -> AuthRegistry:
    """
    Resolves secrets for all auth profiles.
    """
    pass

class AuthRegistry:
    def get_key(self, auth_profile: str) -> str:
        """
        Returns the key for the given profile.
        """
        pass
```
