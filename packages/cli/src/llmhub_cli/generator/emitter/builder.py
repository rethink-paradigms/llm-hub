"""
SP10 - Machine Config Emitter: Config builder and writer.

Builds MachineConfig from selections and writes to YAML.
"""
from pathlib import Path
from typing import List, Dict
import yaml
from llmhub_cli.generator.spec import ProjectSpec
from llmhub_cli.generator.selection import SelectionResult
from .models import (
    MachineConfig,
    MachineProviderConfig,
    MachineRoleConfig,
    MachineRoleMeta,
)


def build_machine_config(
    spec: ProjectSpec,
    selections: List[SelectionResult]
) -> MachineConfig:
    """
    Build MachineConfig from ProjectSpec and SelectionResults.
    
    Args:
        spec: Original ProjectSpec
        selections: List of SelectionResult for each role
        
    Returns:
        MachineConfig ready for runtime
    """
    # Build providers dict
    providers: Dict[str, MachineProviderConfig] = {}
    
    # Start with providers from spec
    if spec.providers:
        for provider_name, provider_spec in spec.providers.items():
            providers[provider_name] = MachineProviderConfig(
                env_key=provider_spec.env_key
            )
    
    # Add providers from selections
    for selection in selections:
        if selection.primary_provider and selection.primary_provider not in providers:
            # Infer env_key from provider name
            env_key_map = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "mistral": "MISTRAL_API_KEY",
            }
            env_key = env_key_map.get(selection.primary_provider.lower())
            providers[selection.primary_provider] = MachineProviderConfig(env_key=env_key)
    
    # Build roles dict
    roles: Dict[str, MachineRoleConfig] = {}
    meta: Dict[str, MachineRoleMeta] = {}
    
    for selection in selections:
        if selection.primary:
            # Get mode from spec
            role_spec = spec.roles.get(selection.role_id)
            mode = role_spec.kind if role_spec else "chat"
            params = role_spec.mode_params if role_spec and role_spec.mode_params else {}
            
            roles[selection.role_id] = MachineRoleConfig(
                provider=selection.primary_provider,
                model=selection.primary_model,
                mode=mode,
                params=params
            )
            
            # Add metadata
            meta[selection.role_id] = MachineRoleMeta(
                rationale=selection.rationale,
                relaxations_applied=selection.relaxations_applied,
                backups=selection.backups
            )
    
    return MachineConfig(
        project=spec.project,
        env=spec.env,
        providers=providers,
        roles=roles,
        meta=meta if meta else None
    )


def write_machine_config(path: str, config: MachineConfig) -> None:
    """
    Write MachineConfig to YAML file.
    
    Args:
        path: Output file path
        config: MachineConfig to write
    """
    file_path = Path(path)
    
    # Convert to dict
    data = config.model_dump(exclude_none=True)
    
    # Write YAML
    with open(file_path, 'w') as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        )
