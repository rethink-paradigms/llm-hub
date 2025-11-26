from typing import List
from .types import ProviderModel

class BaseAdapter:
    def list_models(self, auth_key: str, api_base: str) -> List[ProviderModel]:
        raise NotImplementedError

class OpenAIAdapter(BaseAdapter):
    def list_models(self, auth_key: str, api_base: str) -> List[ProviderModel]:
        # Placeholder implementation
        return [
            ProviderModel(provider="openai", model_id="gpt-4", mode="chat", max_context=8192),
            ProviderModel(provider="openai", model_id="gpt-4.1-mini", mode="chat", max_context=128000),
            ProviderModel(provider="openai", model_id="text-embedding-3-large", mode="embedding"),
        ]

class GeminiAdapter(BaseAdapter):
    def list_models(self, auth_key: str, api_base: str) -> List[ProviderModel]:
        return [
            ProviderModel(provider="gemini", model_id="gemini-pro", mode="chat", max_context=32000),
        ]

class AnthropicAdapter(BaseAdapter):
    def list_models(self, auth_key: str, api_base: str) -> List[ProviderModel]:
        return [
            ProviderModel(provider="anthropic", model_id="claude-3-5-sonnet", mode="chat", max_context=200000),
        ]

class DeepSeekAdapter(BaseAdapter):
    def list_models(self, auth_key: str, api_base: str) -> List[ProviderModel]:
        return [
            ProviderModel(provider="deepseek", model_id="deepseek-chat", mode="chat", max_context=32000),
        ]

class QwenAdapter(BaseAdapter):
    def list_models(self, auth_key: str, api_base: str) -> List[ProviderModel]:
        return [
            ProviderModel(provider="qwen", model_id="qwen-turbo", mode="chat", max_context=32000),
        ]

ADAPTER_MAP = {
    "openai_adapter": OpenAIAdapter,
    "gemini_adapter": GeminiAdapter,
    "anthropic_adapter": AnthropicAdapter,
    "deepseek_adapter": DeepSeekAdapter,
    "qwen_adapter": QwenAdapter,
}
