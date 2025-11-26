from typing import List, Dict, Optional
from src.sp1_config_loader.types import StaticConfig
from src.sp2_auth_registry.registry import AuthRegistry
from .types import ProviderModel
from .adapters import ADAPTER_MAP

class ModelCatalog:
    def __init__(self, models: List[ProviderModel]):
        self.models = models
        self._index: Dict[tuple, ProviderModel] = {
            (m.provider, m.model_id): m for m in models
        }

    def get_model(self, provider: str, model_id: str) -> Optional[ProviderModel]:
        return self._index.get((provider, model_id))

def build_model_catalog(static_config: StaticConfig, auth_registry: AuthRegistry) -> ModelCatalog:
    models = []

    for provider_config in static_config.providers:
        adapter_cls = ADAPTER_MAP.get(provider_config.adapter)
        if not adapter_cls:
            # Log warning or skip
            continue
            
        adapter = adapter_cls()
        auth_key = auth_registry.get_key(provider_config.auth_profile)
        
        # In a real scenario, we'd catch errors here to avoid crashing if one provider fails
        try:
            provider_models = adapter.list_models(auth_key, provider_config.api_base)
            # Ensure provider name matches config
            for m in provider_models:
                m.provider = provider_config.name
            models.extend(provider_models)
        except Exception as e:
            print(f"Failed to list models for {provider_config.name}: {e}")
    
    return ModelCatalog(models)
