"""
Catalog schema definitions.

Defines all data models used within Catalog, including raw source records
and the canonical model representation.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AnyLLMModel(BaseModel):
    """Model discovered from any-llm."""
    provider: str
    model_id: str


class ModelsDevModel(BaseModel):
    """Model metadata from models.dev/api.json."""
    canonical_id: str
    provider: str
    model_id: str
    family: Optional[str] = None
    display_name: Optional[str] = None
    
    # Capabilities
    supports_reasoning: bool = False
    supports_tool_call: bool = False
    supports_structured_output: bool = False
    input_modalities: list[str] = Field(default_factory=lambda: ["text"])
    output_modalities: list[str] = Field(default_factory=lambda: ["text"])
    attachments: list[str] = Field(default_factory=list)
    
    # Limits
    context_tokens: Optional[int] = None
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None
    
    # Pricing (per million tokens)
    price_input_per_million: Optional[float] = None
    price_output_per_million: Optional[float] = None
    price_reasoning_per_million: Optional[float] = None
    
    # Meta
    knowledge_cutoff: Optional[str] = None
    release_date: Optional[str] = None
    last_updated: Optional[str] = None
    open_weights: bool = False


class ArenaModel(BaseModel):
    """Model quality scores from LMArena catalog."""
    arena_id: str
    rating: float
    rating_q025: Optional[float] = None
    rating_q975: Optional[float] = None
    category: str = "overall_text"


class FusedRaw(BaseModel):
    """Intermediate fused record from all sources."""
    canonical_id: str
    anyllm: AnyLLMModel
    modelsdev: Optional[ModelsDevModel] = None
    arena: Optional[ArenaModel] = None


class CanonicalModel(BaseModel):
    """
    Canonical model representation with enriched metadata and derived tiers.
    This is the core business object used by the generator and UI.
    """
    # Basic identity
    canonical_id: str
    provider: str
    model_id: str
    family: Optional[str] = None
    display_name: Optional[str] = None
    
    # Capabilities
    supports_reasoning: bool = False
    supports_tool_call: bool = False
    supports_structured_output: bool = False
    input_modalities: list[str] = Field(default_factory=lambda: ["text"])
    output_modalities: list[str] = Field(default_factory=lambda: ["text"])
    attachments: list[str] = Field(default_factory=list)
    
    # Limits
    context_tokens: Optional[int] = None
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None
    
    # Pricing (per million tokens)
    price_input_per_million: Optional[float] = None
    price_output_per_million: Optional[float] = None
    price_reasoning_per_million: Optional[float] = None
    
    # Derived tiers (1-5, where 1 is best/lowest cost, 5 is worst/highest cost)
    quality_tier: int = 3  # Default to medium
    reasoning_tier: int = 3
    creative_tier: int = 3
    cost_tier: int = 3
    
    # Quality scores
    arena_score: Optional[float] = None
    arena_ci_low: Optional[float] = None
    arena_ci_high: Optional[float] = None
    
    # Meta
    knowledge_cutoff: Optional[str] = None
    release_date: Optional[str] = None
    last_updated: Optional[str] = None
    open_weights: bool = False
    tags: list[str] = Field(default_factory=list)


class Catalog(BaseModel):
    """Complete catalog of available models with metadata."""
    catalog_version: int = 1
    built_at: str
    models: list[CanonicalModel] = Field(default_factory=list)
