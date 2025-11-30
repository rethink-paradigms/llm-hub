from pathlib import Path
from typing import Optional
from pydantic import BaseModel


class ContextOverrides(BaseModel):
    """Optional path overrides from CLI flags."""
    root: Optional[Path] = None
    spec_path: Optional[Path] = None
    runtime_path: Optional[Path] = None
    env_example_path: Optional[Path] = None


class ProjectContext(BaseModel):
    """Resolved project context with all paths."""
    root: Path
    spec_path: Path
    runtime_path: Path
    env_example_path: Path


class ContextError(Exception):
    """Raised when project context cannot be resolved."""
    pass


def _find_project_root(start: Path) -> Optional[Path]:
    """
    Walk upwards from start path to detect project root.
    Priority: directory containing llmhub.spec.yaml, else .git, else pyproject.toml.
    """
    current = start.resolve()
    
    # Check if current directory or any parent contains markers
    for path in [current] + list(current.parents):
        # First priority: llmhub.spec.yaml
        if (path / "llmhub.spec.yaml").exists():
            return path
        # Second priority: .git directory
        if (path / ".git").exists():
            return path
        # Third priority: pyproject.toml
        if (path / "pyproject.toml").exists():
            return path
    
    return None


def resolve_context(
    start: Optional[Path] = None,
    overrides: Optional[ContextOverrides] = None
) -> ProjectContext:
    """
    Resolve project context paths.
    
    Args:
        start: Starting directory for resolution (defaults to cwd).
        overrides: Optional explicit path overrides from CLI.
    
    Returns:
        ProjectContext with resolved paths.
    
    Raises:
        ContextError: If project root cannot be determined.
    """
    if overrides is None:
        overrides = ContextOverrides()
    
    # Determine root
    if overrides.root:
        root = overrides.root.resolve()
    else:
        start_path = start.resolve() if start else Path.cwd()
        root = _find_project_root(start_path)
        if root is None:
            # Fall back to current directory if no markers found
            root = start_path
    
    # Derive paths
    spec_path = overrides.spec_path or (root / "llmhub.spec.yaml")
    runtime_path = overrides.runtime_path or (root / "llmhub.yaml")
    env_example_path = overrides.env_example_path or (root / ".env.example")
    
    return ProjectContext(
        root=root,
        spec_path=spec_path,
        runtime_path=runtime_path,
        env_example_path=env_example_path
    )
