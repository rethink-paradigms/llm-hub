from typing import Dict, Optional

from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    auth_profile: str = Field(..., description="Auth profile name used to resolve API key")
    api_base: Optional[str] = Field(
        None, description="Optional base URL for the provider API"
    )

    class Config:
        extra = "forbid"


class RoleBinding(BaseModel):
    provider: str = Field(..., description="Provider key to use from providers map")
    model: str = Field(..., description="Model identifier to invoke for this role")

    class Config:
        extra = "forbid"


class OrchestratorConfig(BaseModel):
    project: str
    env: str
    providers: Dict[str, ProviderConfig]
    roles: Dict[str, RoleBinding]

    class Config:
        extra = "forbid"
