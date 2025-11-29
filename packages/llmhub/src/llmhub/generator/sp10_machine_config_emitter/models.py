"""SP10 - Machine Config Emitter: Data models."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class MachineProviderConfig(BaseModel):
    """Provider configuration in machine config."""
    env_key: Optional[str] = None


class MachineRoleConfig(BaseModel):
    """Role configuration in machine config."""
    provider: str
    model: str
    mode: str = "chat"
    params: Dict[str, Any] = Field(default_factory=dict)


class MachineRoleMeta(BaseModel):
    """Metadata about role selection."""
    rationale: Optional[str] = None
    relaxations_applied: List[str] = Field(default_factory=list)
    backups: List[str] = Field(default_factory=list)


class MachineConfig(BaseModel):
    """
    Machine-readable configuration for LLM Hub Runtime.
    
    This is the output of the generator, ready to be consumed by the runtime.
    """
    project: str
    env: str
    providers: Dict[str, MachineProviderConfig]
    roles: Dict[str, MachineRoleConfig]
    meta: Optional[Dict[str, MachineRoleMeta]] = Field(default=None)
