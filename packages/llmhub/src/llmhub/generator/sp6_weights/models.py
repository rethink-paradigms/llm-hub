"""SP6 - Weights: Weights data model."""
from pydantic import BaseModel, Field, field_validator


class Weights(BaseModel):
    """Normalized weights for scoring dimensions."""
    w_quality: float = Field(ge=0.0, le=1.0)
    w_cost: float = Field(ge=0.0, le=1.0)
    w_reasoning: float = Field(ge=0.0, le=1.0)
    w_creative: float = Field(ge=0.0, le=1.0)
    w_context: float = Field(ge=0.0, le=1.0)
    w_freshness: float = Field(ge=0.0, le=1.0)
    
    @field_validator("w_quality", "w_cost", "w_reasoning", "w_creative", "w_context", "w_freshness")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """Ensure weights are in valid range."""
        return max(0.0, min(1.0, v))
