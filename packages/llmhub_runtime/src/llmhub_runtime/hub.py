import os
from typing import Optional, Dict, Any, List, Union, Callable, Iterator, AsyncIterator
from .models import RuntimeConfig, ResolvedCall
from .config_loader import load_runtime_config
from .resolver import resolve_role
from .errors import EnvVarMissingError
try:
    import any_llm
except ImportError:
    # Fallback or strict requirement handled at runtime or via package dependencies
    any_llm = None

# Internal types for hooks
CallContext = Dict[str, Any]
CallResult = Dict[str, Any]

class LLMHub:
    def __init__(
        self,
        config_path: Optional[str] = None,
        config_obj: Optional[RuntimeConfig] = None,
        strict_env: bool = False,
        on_before_call: Optional[Callable[[CallContext], None]] = None,
        on_after_call: Optional[Callable[[CallResult], None]] = None,
    ):
        """
        Initialize the LLMHub client.

        Args:
            config_path: Path to the llmhub.yaml file.
            config_obj: Pre-loaded RuntimeConfig object.
            strict_env: If True, check that all env_key vars exist on init.
            on_before_call: Hook to run before calling any-llm.
            on_after_call: Hook to run after calling any-llm.

        Raises:
            ValueError: If neither or both config_path and config_obj are provided.
            EnvVarMissingError: If strict_env is True and an environment variable is missing.
        """
        if (config_path is None) == (config_obj is None):
             raise ValueError("Exactly one of config_path or config_obj must be provided.")

        if config_path:
            self.config = load_runtime_config(config_path)
        else:
            self.config = config_obj

        self.strict_env = strict_env
        self.on_before_call = on_before_call
        self.on_after_call = on_after_call

        if self.strict_env:
            self._validate_env_vars()

    def _validate_env_vars(self):
        for provider_name, provider_config in self.config.providers.items():
            if provider_config.env_key:
                if provider_config.env_key not in os.environ:
                    raise EnvVarMissingError(f"Missing environment variable: {provider_config.env_key} for provider {provider_name}")

    def completion(
        self,
        role: str,
        messages: List[Dict[str, Any]],
        params_override: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Perform a chat completion for the given role.

        Args:
            role: The role name.
            messages: List of chat messages.
            params_override: Optional parameters to override defaults.

        Returns:
            The raw response from any-llm.
        """
        resolved = resolve_role(self.config, role, params_override)

        # Prepare context for hook
        call_context: CallContext = {
            "role": resolved.role,
            "provider": resolved.provider,
            "model": resolved.model,
            "mode": resolved.mode,
            "params": resolved.params,
            "messages": messages
        }

        if self.on_before_call:
            self.on_before_call(call_context)

        success = False
        error = None
        response = None
        # Simple timing could be added here if needed for duration_ms

        try:
            if any_llm is None:
                 raise ImportError("any-llm-sdk is not installed. Please install it with 'pip install any-llm-sdk'.")

            response = any_llm.completion(
                provider=resolved.provider,
                model=resolved.model,
                messages=messages,
                **resolved.params
            )
            success = True
            return response
        except Exception as e:
            error = e
            raise e
        finally:
            if self.on_after_call:
                result: CallResult = {
                    "role": resolved.role,
                    "provider": resolved.provider,
                    "model": resolved.model,
                    "mode": resolved.mode,
                    # "duration_ms": ... # Not implementing timing for now as not explicitly asked beyond spec details
                    "success": success,
                    "error": error,
                    "response": response
                }
                self.on_after_call(result)

    def embedding(
        self,
        role: str,
        input: Union[str, List[str]],
        params_override: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Generate embeddings for the given input using the specified role.

        Args:
            role: The role name.
            input: Input text or list of texts.
            params_override: Optional parameters to override defaults.

        Returns:
             The raw response from any-llm.
        """
        resolved = resolve_role(self.config, role, params_override)

        call_context: CallContext = {
            "role": resolved.role,
            "provider": resolved.provider,
            "model": resolved.model,
            "mode": resolved.mode,
            "params": resolved.params,
            "input": input
        }

        if self.on_before_call:
            self.on_before_call(call_context)

        success = False
        error = None
        response = None

        try:
            if any_llm is None:
                 raise ImportError("any-llm-sdk is not installed. Please install it with 'pip install any-llm-sdk'.")

            response = any_llm.embedding(
                provider=resolved.provider,
                model=resolved.model,
                inputs=input, # any-llm uses 'inputs' for embedding
                **resolved.params
            )
            success = True
            return response
        except Exception as e:
            error = e
            raise e
        finally:
             if self.on_after_call:
                result: CallResult = {
                    "role": resolved.role,
                    "provider": resolved.provider,
                    "model": resolved.model,
                    "mode": resolved.mode,
                    "success": success,
                    "error": error,
                    "response": response
                }
                self.on_after_call(result)
