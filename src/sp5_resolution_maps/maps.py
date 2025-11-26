from typing import Dict
from src.sp1_config_loader.types import StaticConfig
from src.sp3_model_catalog.catalog import ModelCatalog
from src.sp4_storage_catalog.catalog import StorageCatalog
from .types import ResolutionMaps, LLMResolution, StoreResolution, ResolutionStatus

def build_resolution_maps(
    static_config: StaticConfig,
    model_catalog: ModelCatalog,
    storage_catalog: StorageCatalog
) -> ResolutionMaps:
    llm_map = {}
    store_map = {}

    for project in static_config.projects:
        for env_name, env_config in project.envs.items():
            # Resolve LLM
            for role, binding in env_config.llm.items():
                key = (project.name, env_name, role)
                model_def = model_catalog.get_model(binding.provider, binding.model_id)
                
                if model_def:
                    llm_map[key] = LLMResolution(
                        status=ResolutionStatus.OK,
                        config=model_def.model_dump()
                    )
                else:
                    llm_map[key] = LLMResolution(
                        status=ResolutionStatus.ERROR,
                        message=f"Model {binding.provider}/{binding.model_id} not found in catalog"
                    )

            # Resolve Storage
            for role, binding in env_config.storage.items():
                key = (project.name, env_name, role)
                store_config = storage_catalog.get_store_config(project.name, env_name, role)
                
                if store_config:
                    store_map[key] = StoreResolution(
                        status=ResolutionStatus.OK,
                        config=store_config.model_dump()
                    )
                else:
                    store_map[key] = StoreResolution(
                        status=ResolutionStatus.ERROR,
                        message="Storage config not found in catalog"
                    )

    return ResolutionMaps(llm=llm_map, store=store_map)
