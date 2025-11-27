from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMResponse(BaseModel):
    content: str
    raw: Any = Field(..., description="Full provider-specific response payload")
    provider: str
    model: str


class ResolvedLLMConfig(BaseModel):
    provider: str
    model: str
    api_key: str
    api_base: Optional[str] = None
