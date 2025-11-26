from typing import List, Optional
from pydantic import BaseModel

class ResolveOptions(BaseModel):
    fallbacks: Optional[List[str]] = None
