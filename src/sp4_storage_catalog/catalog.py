from typing import Dict, Optional
from src.sp1_config_loader.types import StaticConfig
from .types import StoreConfig

class StorageCatalog:
    def __init__(self, configs: Dict[tuple, StoreConfig]):
        # Key: (project, env, role)
        self._configs = configs

    def get_store_config(self, project: str, env: str, role: str) -> Optional[StoreConfig]:
        return self._configs.get((project, env, role))

def build_storage_catalog(static_config: StaticConfig) -> StorageCatalog:
    configs = {}

    for project in static_config.projects:
        for env_name, env_config in project.envs.items():
            for role, binding in env_config.storage.items():
                config = StoreConfig(
                    project=project.name,
                    env=env_name,
                    role=role,
                    backend=binding.backend,
                    dsn=binding.dsn
                )
                configs[(project.name, env_name, role)] = config

    return StorageCatalog(configs)
