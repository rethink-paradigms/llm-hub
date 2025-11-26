from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..runtime.types import Message, LLMResponse

class BaseProviderAdapter(ABC):
    @abstractmethod
    def run_chat(self, model: str, messages: List[Message], params: Dict[str, Any], api_key: str, api_base: Optional[str] = None) -> LLMResponse:
        pass
