import pytest
from pathlib import Path
import tempfile
import shutil
from llmhub_cli.context import resolve_context, ContextOverrides, _find_project_root


def test_find_project_root_with_spec(tmp_path):
    """Test finding project root with spec file."""
    spec_file = tmp_path / "llmhub.spec.yaml"
    spec_file.touch()
    
    root = _find_project_root(tmp_path)
    assert root == tmp_path


def test_find_project_root_with_git(tmp_path):
    """Test finding project root with .git directory."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    
    root = _find_project_root(tmp_path)
    assert root == tmp_path


def test_find_project_root_with_pyproject(tmp_path):
    """Test finding project root with pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.touch()
    
    root = _find_project_root(tmp_path)
    assert root == tmp_path


def test_find_project_root_walks_up(tmp_path):
    """Test that root finding walks up directory tree."""
    spec_file = tmp_path / "llmhub.spec.yaml"
    spec_file.touch()
    
    subdir = tmp_path / "sub" / "dir"
    subdir.mkdir(parents=True)
    
    root = _find_project_root(subdir)
    assert root == tmp_path


def test_resolve_context_defaults(tmp_path):
    """Test resolving context with defaults."""
    context = resolve_context(start=tmp_path)
    
    # Root should be tmp_path or a parent
    assert context.root is not None
    assert context.spec_path.name == "llmhub.spec.yaml"
    assert context.runtime_path.name == "llmhub.yaml"
    assert context.env_example_path.name == ".env.example"


def test_resolve_context_with_overrides(tmp_path):
    """Test resolving context with explicit overrides."""
    custom_spec = tmp_path / "custom.spec.yaml"
    custom_runtime = tmp_path / "custom.yaml"
    
    overrides = ContextOverrides(
        root=tmp_path,
        spec_path=custom_spec,
        runtime_path=custom_runtime
    )
    
    context = resolve_context(start=tmp_path, overrides=overrides)
    
    assert context.root == tmp_path
    assert context.spec_path == custom_spec
    assert context.runtime_path == custom_runtime


def test_resolve_context_spec_path_derivation(tmp_path):
    """Test that spec/runtime paths are derived from root."""
    context = resolve_context(start=tmp_path)
    
    assert context.spec_path == context.root / "llmhub.spec.yaml"
    assert context.runtime_path == context.root / "llmhub.yaml"
    assert context.env_example_path == context.root / ".env.example"
