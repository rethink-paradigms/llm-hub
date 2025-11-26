import os
import yaml
from typing import List, Dict
from .types import StaticConfig, ProviderConfig, ProjectConfig, RoleRegistry, EnvConfig, LLMRoleBinding, StoreRoleBinding

def load_yaml(path: str) -> Dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def load_static_config(config_dir: str) -> StaticConfig:
    providers_path = os.path.join(config_dir, "providers.yaml")
    projects_path = os.path.join(config_dir, "projects.yaml")
    roles_path = os.path.join(config_dir, "roles.yaml")

    # Load raw data
    providers_data = load_yaml(providers_path)
    projects_data = load_yaml(projects_path)
    
    roles_data = {"roles": {}}
    if os.path.exists(roles_path):
        roles_data = load_yaml(roles_path)

    # Parse Providers
    providers = [ProviderConfig(**p) for p in providers_data.get('providers', [])]
    
    # Parse Projects
    projects = []
    for p_name, p_data in projects_data.get('projects', {}).items():
        envs = {}
        for env_name, env_data in p_data.get('envs', {}).items():
            llm_bindings = {}
            for role, binding in env_data.get('llm', {}).items():
                llm_bindings[role] = LLMRoleBinding(**binding)
            
            store_bindings = {}
            for role, binding in env_data.get('storage', {}).items():
                store_bindings[role] = StoreRoleBinding(**binding)
                
            envs[env_name] = EnvConfig(llm=llm_bindings, storage=store_bindings)
            
        projects.append(ProjectConfig(name=p_name, envs=envs))

    # Parse Roles
    roles = RoleRegistry(roles=roles_data.get('roles', {}))

    return StaticConfig(
        providers=providers,
        projects=projects,
        roles=roles
    )
