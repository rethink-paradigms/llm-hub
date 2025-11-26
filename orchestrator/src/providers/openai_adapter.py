from typing import List, Dict, Any, Optional
from openai import OpenAI
from ..runtime.types import Message, LLMResponse
from .base import BaseProviderAdapter
from ..utils.errors import ProviderError

class OpenAIAdapter(BaseProviderAdapter):
    def run_chat(self, model: str, messages: List[Message], params: Dict[str, Any], api_key: str, api_base: Optional[str] = None) -> LLMResponse:
        try:
            client = OpenAI(api_key=api_key, base_url=api_base)
            
            # Convert pydantic messages to dicts
            msgs = [{"role": m.role, "content": m.content} for m in messages]
            
            response = client.chat.completions.create(
                model=model,
                messages=msgs,
                **params
            )
            
            content = response.choices[0].message.content
            
            return LLMResponse(
                content=content,
                raw=response,
                provider="openai",
                model=model
            )
        except Exception as e:
            raise ProviderError(f"OpenAI call failed: {str(e)}")
