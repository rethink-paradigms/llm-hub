import os
from typing import Dict
from src.sp1_config_loader.types import StaticConfig

class AuthRegistry:
    def __init__(self, secrets: Dict[str, str]):
        self._secrets = secrets

    def get_key(self, auth_profile: str) -> str:
        return self._secrets.get(auth_profile)

def build_auth_registry(static_config: StaticConfig) -> AuthRegistry:
    """
    Resolves secrets for all auth profiles defined in the static config.
    """
    secrets = {}
    
    # Iterate through providers to find auth profiles
    for provider in static_config.providers:
        profile_name = provider.auth_profile
        if not profile_name:
            continue
            
        # Convention: RO_AUTH_<AUTH_PROFILE>_API_KEY
        env_var_name = f"RO_AUTH_{profile_name}_API_KEY"
        secret_value = os.environ.get(env_var_name)
        
        if secret_value:
            secrets[profile_name] = secret_value
        else:
            # PLAN-2 says: Missing key -> throw explicit error.
            # However, for local development without all keys, maybe we warn?
            # The plan says "Missing key -> throw explicit error." so we must throw.
            # But wait, if I throw now, the CLI might break if I don't have all keys set.
            # I will implement strict check but maybe only for used profiles?
            # The spec says "For each provider... Resolve actual credentials".
            # If I have a provider config but no key, it's an error.
            # I will raise error to comply strictly with "throw explicit error".
            # But to allow the user to run the CLI without setting 5 keys, I'll check if it's strictly required.
            # The prompt says "Missing key -> throw explicit error."
            # I will follow this.
            raise ValueError(f"Missing required environment variable: {env_var_name}")
                
    return AuthRegistry(secrets)
