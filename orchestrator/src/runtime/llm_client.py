from typing import List, Dict, Any, Optional
from ..config.loader import load_config
from ..config.schema import OrchestratorConfig
from ..resolution.resolver import resolve_llm_config
from ..providers.openai_adapter import OpenAIAdapter
from ..providers.gemini_adapter import GeminiAdapter
from ..providers.anthropic_adapter import AnthropicAdapter
from ..providers.deepseek_adapter import DeepSeekAdapter
from ..providers.qwen_adapter import QwenAdapter
from ..providers.openrouter_adapter import OpenRouterAdapter
from ..utils.errors import ProviderError
from .types import Message, LLMResponse

class LLMClient:
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self._adapters = {
            "openai": OpenAIAdapter(),
            "gemini": GeminiAdapter(),
            "anthropic": AnthropicAdapter(),
            "deepseek": DeepSeekAdapter(),
            "qwen": QwenAdapter(),
            "openrouter": OpenRouterAdapter(),
        }

    def run(self, role: str, messages: List[Message], params_override: Optional[Dict[str, Any]] = None) -> LLMResponse:
        # 1. Resolve config
        resolved = resolve_llm_config(self.config, role)
        
        # 2. Get adapter
        adapter = self._adapters.get(resolved.provider)
        if not adapter:
            raise ProviderError(f"Unknown provider: {resolved.provider}")
        
        # 3. Prepare params
        params = params_override or {}
        
        # 4. Call adapter
        return adapter.run_chat(
            model=resolved.model,
            messages=messages,
            params=params,
            api_key=resolved.api_key,
            api_base=resolved.api_base
        )

def get_llm_client(config_path: str) -> LLMClient:
    """
    Factory function to create an LLMClient from a config file.
    """
    config = load_config(config_path)
    return LLMClient(config)
