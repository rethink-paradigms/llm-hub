from typing import Dict, Optional, Any
from pydantic import BaseModel
from enum import Enum

class ResolutionStatus(str, Enum):
    OK = "ok"
    ERROR = "error"

class LLMResolution(BaseModel):
    status: ResolutionStatus
    config: Optional[Dict[str, Any]] = None # The resolved config (provider, model, etc.)
    message: Optional[str] = None

class StoreResolution(BaseModel):
    status: ResolutionStatus
    config: Optional[Dict[str, Any]] = None # The resolved store config
    message: Optional[str] = None

class ResolutionMaps(BaseModel):
    # Key: (project, env, role)
    llm: Dict[tuple, LLMResolution]
    store: Dict[tuple, StoreResolution]
