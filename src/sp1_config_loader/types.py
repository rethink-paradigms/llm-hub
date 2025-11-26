from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field

class ProviderConfig(BaseModel):
    name: str
    kind: str  # "llm"
    auth_profile: str
    api_base: Optional[str] = None
    adapter: str

class LLMRoleBinding(BaseModel):
    provider: str
    model_id: str
    mode: str
    auth_profile: str

class StoreRoleBinding(BaseModel):
    kind: str
    backend: str
    dsn: str

class EnvConfig(BaseModel):
    llm: Dict[str, LLMRoleBinding] = Field(default_factory=dict)
    storage: Dict[str, StoreRoleBinding] = Field(default_factory=dict)

class ProjectConfig(BaseModel):
    name: str
    envs: Dict[str, EnvConfig]

class RoleRegistry(BaseModel):
    roles: Dict[str, Dict[str, str]] # role_name -> {type: ...}

class StaticConfig(BaseModel):
    providers: List[ProviderConfig]
    projects: List[ProjectConfig]
    roles: RoleRegistry
