class LLMHubRuntimeError(Exception):
    """Base class for all runtime errors."""
    pass

class ConfigError(LLMHubRuntimeError):
    """For invalid or unreadable configs."""
    pass

class UnknownRoleError(LLMHubRuntimeError):
    """When an unknown role is requested and no default is configured."""
    pass

class UnknownProviderError(LLMHubRuntimeError):
    """When a role references a provider that isn’t defined in providers."""
    pass

class EnvVarMissingError(LLMHubRuntimeError):
    """If runtime chooses to validate env_key and the required env var is missing."""
    pass
