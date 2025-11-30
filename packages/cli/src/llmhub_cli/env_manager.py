import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from .spec_models import SpecConfig


class MissingEnvVar(BaseModel):
    """Missing environment variable information."""
    provider: str
    env_key: str


def generate_env_example(spec: SpecConfig, path: Path, overwrite: bool = True) -> None:
    """
    Generate .env.example file from spec providers.
    
    Args:
        spec: SpecConfig with provider definitions.
        path: Path to write .env.example.
        overwrite: Whether to overwrite existing file.
    
    Raises:
        FileExistsError: If file exists and overwrite is False.
    """
    if path.exists() and not overwrite:
        raise FileExistsError(f".env.example already exists: {path}")
    
    lines = [
        f"# LLMHub generated .env.example for project: {spec.project} (env: {spec.env})",
        ""
    ]
    
    for provider_name, provider_config in spec.providers.items():
        if provider_config.env_key:
            # Add comment with provider name
            lines.append(f"# {provider_name.capitalize()} API key")
            lines.append(f"{provider_config.env_key}=")
            lines.append("")
    
    with open(path, 'w') as f:
        f.write('\n'.join(lines))


def check_env(spec: SpecConfig, load_dotenv_path: Optional[Path] = None) -> list[MissingEnvVar]:
    """
    Check for missing environment variables required by spec.
    
    Args:
        spec: SpecConfig with provider definitions.
        load_dotenv_path: Optional path to .env file to load before checking.
    
    Returns:
        List of missing environment variables.
    """
    # Optionally load .env file
    if load_dotenv_path and load_dotenv_path.exists():
        load_dotenv(load_dotenv_path)
    
    missing = []
    
    for provider_name, provider_config in spec.providers.items():
        if provider_config.enabled and provider_config.env_key:
            if provider_config.env_key not in os.environ:
                missing.append(MissingEnvVar(
                    provider=provider_name,
                    env_key=provider_config.env_key
                ))
    
    return missing
