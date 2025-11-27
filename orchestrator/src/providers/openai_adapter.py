from typing import Any, Dict, List, Optional

from openai import OpenAI

from ..runtime.types import LLMResponse, Message
from ..utils.errors import ProviderError
from .base import BaseProviderAdapter


class OpenAIAdapter(BaseProviderAdapter):
    def run_chat(
        self,
        model: str,
        messages: List[Message],
        params: Dict[str, Any],
        api_key: str,
        api_base: Optional[str] = None,
    ) -> LLMResponse:
        """
        Minimal OpenAI chat completion call using the official SDK.
        """
        try:
            client = OpenAI(api_key=api_key, base_url=api_base)
            serialized_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            response = client.chat.completions.create(
                model=model,
                messages=serialized_messages,
                **(params or {}),
            )

            content = response.choices[0].message.content
            return LLMResponse(content=content, raw=response, provider="openai", model=model)
        except Exception as exc:
            raise ProviderError(f"OpenAI call failed: {exc}") from exc
