from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel

class LLMMode(str, Enum):
    chat = "chat"
    embedding = "embedding"
    image = "image"
    audio = "audio"
    tool = "tool"
    other = "other"

class ProviderConfig(BaseModel):
    env_key: Optional[str] = None

class RoleConfig(BaseModel):
    provider: str
    model: str
    mode: LLMMode
    params: Dict[str, Any] = {}

class RoleDefaultsConfig(BaseModel):
    provider: str
    model: str
    mode: LLMMode
    params: Dict[str, Any] = {}

class RuntimeConfig(BaseModel):
    project: str
    env: str
    providers: Dict[str, ProviderConfig]
    roles: Dict[str, RoleConfig]
    defaults: Optional[RoleDefaultsConfig] = None

class ResolvedCall(BaseModel):
    role: str
    provider: str
    model: str
    mode: LLMMode
    params: Dict[str, Any]
