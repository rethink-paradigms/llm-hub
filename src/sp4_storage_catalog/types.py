from typing import Optional
from pydantic import BaseModel

class StoreConfig(BaseModel):
    project: str
    env: str
    role: str
    backend: str
    dsn: str
