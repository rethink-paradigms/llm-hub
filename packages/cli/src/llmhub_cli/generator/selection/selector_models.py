"""SP9 - Selector Orchestrator: Data models."""
from typing import Optional, List
from pydantic import BaseModel, Field


class SelectorOptions(BaseModel):
    """Options for model selection."""
    num_backups: int = Field(default=2, ge=0, description="Number of backup models to select")
    require_primary: bool = Field(default=True, description="Fail if no primary model found")


class SelectionResult(BaseModel):
    """Result of model selection for a role."""
    role_id: str
    primary: Optional[str] = None  # canonical_id
    primary_provider: Optional[str] = None
    primary_model: Optional[str] = None
    primary_score: Optional[float] = None
    backups: List[str] = Field(default_factory=list)  # List of canonical_ids
    rationale: Optional[str] = None
    relaxations_applied: List[str] = Field(default_factory=list)
