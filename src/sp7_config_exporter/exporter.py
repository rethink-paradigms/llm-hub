import json
import yaml
from typing import Dict, Any, List, Union
from pydantic import BaseModel
from src.sp5_resolution_maps.types import ResolutionMaps, ResolutionStatus

class ExportedConfig(BaseModel):
    project: str
    env: str
    llm: Dict[str, Any]
    store: Dict[str, Any]
    errors: List[str]

def export_config(
    resolution_maps: ResolutionMaps,
    project: str,
    env: str,
    format: str
) -> Union[str, Dict]:
    """
    Exports the configuration for the specified context in the requested format.
    """
    llm_configs = {}
    store_configs = {}
    errors = []

    # Gather LLM configs
    for (p, e, role), res in resolution_maps.llm.items():
        if p == project and e == env:
            if res.status == ResolutionStatus.OK and res.config:
                llm_configs[role] = res.config
            else:
                errors.append(f"LLM Role {role}: {res.message}")

    # Gather Store configs
    for (p, e, role), res in resolution_maps.store.items():
        if p == project and e == env:
            if res.status == ResolutionStatus.OK and res.config:
                store_configs[role] = res.config
            else:
                errors.append(f"Store Role {role}: {res.message}")

    # Build structured object
    exported = ExportedConfig(
        project=project,
        env=env,
        llm=llm_configs,
        store=store_configs,
        errors=errors
    )

    if format == "json":
        return exported.model_dump_json(indent=2)
    elif format == "yaml":
        return yaml.dump(exported.model_dump(), sort_keys=False)
    elif format == "env":
        # Flatten to env vars
        # Convention: RO_<ROLE>_<FIELD> (uppercase, dots to underscores)
        lines = []
        
        for role, config in llm_configs.items():
            role_slug = role.upper().replace(".", "_")
            for k, v in config.items():
                key = f"RO_LLM_{role_slug}_{k.upper()}"
                lines.append(f"{key}={v}")
                
        for role, config in store_configs.items():
            role_slug = role.upper().replace(".", "_")
            for k, v in config.items():
                key = f"RO_STORE_{role_slug}_{k.upper()}"
                lines.append(f"{key}={v}")
                
        return "\n".join(lines)
    else:
        raise ValueError(f"Unsupported format: {format}")
