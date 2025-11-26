import yaml
import os
from .schema import OrchestratorConfig

def load_config(config_path: str) -> OrchestratorConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
        
    return OrchestratorConfig(**data)
