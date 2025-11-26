class OrchestratorError(Exception):
    """Base class for orchestrator errors."""
    pass

class ConfigError(OrchestratorError):
    """Raised when configuration is invalid or missing."""
    pass

class AuthError(OrchestratorError):
    """Raised when authentication fails or keys are missing."""
    pass

class ProviderError(OrchestratorError):
    """Raised when a provider fails or is unknown."""
    pass
