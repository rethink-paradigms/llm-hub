from typing import List, Dict, Any, Optional
from ..runtime.types import Message, LLMResponse
from .base import BaseProviderAdapter

class StubAdapter(BaseProviderAdapter):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    def run_chat(self, model: str, messages: List[Message], params: Dict[str, Any], api_key: str, api_base: Optional[str] = None) -> LLMResponse:
        return LLMResponse(
            content=f"Stub response from {self.provider_name} for model {model}",
            raw={},
            provider=self.provider_name,
            model=model
        )
