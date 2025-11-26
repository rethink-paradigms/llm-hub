from typing import Optional
from pydantic import BaseModel

class ProviderModel(BaseModel):
    provider: str
    model_id: str
    mode: str  # 'chat', 'completion', 'embedding'
    max_context: Optional[int] = None
    cost_band: Optional[str] = None
    latency_band: Optional[str] = None
