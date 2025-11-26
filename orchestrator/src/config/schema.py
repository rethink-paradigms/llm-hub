from typing import Dict, Optional
from pydantic import BaseModel, Field

class ProviderConfig(BaseModel):
    auth_profile: str
    api_base: Optional[str] = None

class RoleBinding(BaseModel):
    provider: str
    model: str

class OrchestratorConfig(BaseModel):
    project: str
    env: str
    providers: Dict[str, ProviderConfig]
    roles: Dict[str, RoleBinding]
