"""
SP3 - Needs Schema: RoleNeed data model.

Defines the canonical RoleNeed model representing interpreted role requirements.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class RoleNeed(BaseModel):
    """
    Canonical role need with all selection criteria.
    
    This model represents the interpreted needs of a role after LLM processing.
    It contains all information needed for model selection, filtering, and scoring.
    """
    model_config = ConfigDict(extra="allow")
    
    # ===== Identity =====
    id: str = Field(..., description="Unique identifier for this role")
    
    # ===== Task Characteristics =====
    task_kind: str = Field(
        default="general",
        description="Type of task: reasoning, creative, factual, chat, etc."
    )
    importance: str = Field(
        default="medium",
        description="Role importance: low, medium, high, critical"
    )
    
    # ===== Selection Weights (0.0-1.0) =====
    quality_bias: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Bias towards quality (0.0=ignore, 1.0=maximize)"
    )
    cost_bias: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Bias towards cost (0.0=ignore, 1.0=minimize cost)"
    )
    latency_sensitivity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Sensitivity to latency (0.0=ignore, 1.0=minimize latency)"
    )
    
    # ===== Capabilities (Hard Constraints) =====
    reasoning_required: bool = Field(
        default=False,
        description="Whether reasoning/chain-of-thought is required"
    )
    tools_required: bool = Field(
        default=False,
        description="Whether tool/function calling is required"
    )
    structured_output_required: bool = Field(
        default=False,
        description="Whether structured JSON output is required"
    )
    
    # ===== Context Requirements =====
    context_min: Optional[int] = Field(
        default=None,
        description="Minimum context window size in tokens"
    )
    
    # ===== Modalities =====
    modalities_in: list[str] = Field(
        default_factory=lambda: ["text"],
        description="Required input modalities (text, image, audio, etc.)"
    )
    modalities_out: list[str] = Field(
        default_factory=lambda: ["text"],
        description="Required output modalities (text, image, audio, etc.)"
    )
    
    # ===== Provider Constraints =====
    provider_allowlist: Optional[list[str]] = Field(
        default=None,
        description="Allowed providers (None = all allowed)"
    )
    provider_blocklist: Optional[list[str]] = Field(
        default=None,
        description="Blocked providers"
    )
    model_denylist: Optional[list[str]] = Field(
        default=None,
        description="Specific models to exclude"
    )
    
    # ===== Tier Preferences (1-5, where 1 is best) =====
    reasoning_tier_pref: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Preferred reasoning tier (1=best, 5=worst)"
    )
    creative_tier_pref: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Preferred creative tier (1=best, 5=worst)"
    )
    
    # ===== Additional Context =====
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes or context from interpretation"
    )
    
    @field_validator("importance")
    @classmethod
    def validate_importance(cls, v: str) -> str:
        """Validate importance level."""
        valid = {"low", "medium", "high", "critical"}
        if v.lower() not in valid:
            # Default to medium if invalid
            return "medium"
        return v.lower()
    
    @field_validator("task_kind")
    @classmethod
    def validate_task_kind(cls, v: str) -> str:
        """Normalize task_kind to lowercase."""
        return v.lower()
