from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class LLMResponse(BaseModel):
    content: str
    raw: Any
    provider: str
    model: str

class ResolvedLLMConfig(BaseModel):
    provider: str
    model: str
    api_key: str
    api_base: Optional[str] = None
