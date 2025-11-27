from typing import Dict, Any, Optional
from .models import RuntimeConfig, ResolvedCall
from .errors import UnknownRoleError, UnknownProviderError

def resolve_role(config: RuntimeConfig, role: str, params_override: Optional[Dict[str, Any]] = None) -> ResolvedCall:
    """
    Map a logical role name to a concrete {provider, model, mode, params}.

    Args:
        config: The runtime configuration.
        role: The role name to resolve.
        params_override: Optional parameters to override the defaults.

    Returns:
        A ResolvedCall object with the resolved details.

    Raises:
        UnknownRoleError: If the role is not found and no default is configured.
        UnknownProviderError: If the role references an undefined provider.
    """
    if role in config.roles:
        base = config.roles[role]
    elif config.defaults is not None:
        base = config.defaults
    else:
        raise UnknownRoleError(f"Role '{role}' not found and no defaults configured.")

    if base.provider not in config.providers:
        raise UnknownProviderError(f"Provider '{base.provider}' referenced by role '{role}' is not defined in providers.")

    params = {**base.params, **(params_override or {})}

    return ResolvedCall(
        role=role,
        provider=base.provider,
        model=base.model,
        mode=base.mode,
        params=params
    )
