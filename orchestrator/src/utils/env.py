import os
import re

from .errors import AuthError


def _format_env_var(auth_profile: str) -> str:
    safe_profile = re.sub(r"[^A-Z0-9]+", "_", auth_profile.upper())
    return f"ORCH_AUTH_{safe_profile}_API_KEY"


def resolve_auth_key(auth_profile: str) -> str:
    """
    Resolves the API key for the given auth profile from environment variables.
    Convention: ORCH_AUTH_<AUTH_PROFILE>_API_KEY
    """
    if not auth_profile:
        raise AuthError("Auth profile is required to resolve API key")

    env_var_name = _format_env_var(auth_profile)
    api_key = os.environ.get(env_var_name)

    if not api_key:
        raise AuthError(
            f"Missing environment variable {env_var_name} for auth profile {auth_profile}"
        )

    return api_key
