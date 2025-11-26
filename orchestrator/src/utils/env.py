import os
from .errors import AuthError

def resolve_auth_key(auth_profile: str) -> str:
    """
    Resolves the API key for the given auth profile from environment variables.
    Convention: ORCH_AUTH_<AUTH_PROFILE>_API_KEY
    """
    env_var_name = f"ORCH_AUTH_{auth_profile.upper()}_API_KEY"
    api_key = os.environ.get(env_var_name)
    
    if not api_key:
        raise AuthError(f"Missing environment variable: {env_var_name} for auth profile: {auth_profile}")
        
    return api_key
