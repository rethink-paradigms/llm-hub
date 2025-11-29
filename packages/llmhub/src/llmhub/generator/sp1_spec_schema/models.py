"""
SP1 - Spec Schema: Data models for human spec.

These models define the structure of the user-written llmhub.spec.yaml file.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ProviderSpec(BaseModel):
    """Provider configuration in spec."""
    model_config = ConfigDict(extra="allow")
    
    enabled: bool = True
    env_key: Optional[str] = None


class Preferences(BaseModel):
    """Role preferences for model selection."""
    model_config = ConfigDict(extra="allow")
    
    latency: Optional[str] = None  # "low", "medium", "high"
    cost: Optional[str] = None  # "low", "medium", "high"
    quality: Optional[str] = None  # "low", "medium", "high"
    providers: Optional[list[str]] = None  # Allowlist
    provider_blocklist: Optional[list[str]] = None
    model_denylist: Optional[list[str]] = None


class DefaultPreferences(BaseModel):
    """Default preferences applied to all roles."""
    model_config = ConfigDict(extra="allow")
    
    providers: Optional[list[str]] = None
    latency: Optional[str] = None
    cost: Optional[str] = None
    quality: Optional[str] = None


class RoleSpec(BaseModel):
    """Specification for a single role in the spec."""
    model_config = ConfigDict(extra="allow")
    
    kind: str  # "chat", "embedding", "image", etc.
    description: str
    preferences: Optional[Preferences] = Field(default_factory=Preferences)
    force_provider: Optional[str] = None
    force_model: Optional[str] = None
    mode_params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProjectSpec(BaseModel):
    """
    Complete project specification from llmhub.spec.yaml.
    
    This is the root model for the human-written spec file.
    """
    model_config = ConfigDict(extra="allow")
    
    project: str
    env: str
    providers: Optional[Dict[str, ProviderSpec]] = Field(default_factory=dict)
    roles: Dict[str, RoleSpec]
    defaults: Optional[DefaultPreferences] = None
