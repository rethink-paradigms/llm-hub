"""
Smoke tests for CLI commands.
Tests basic workflow: init -> generate -> env sync
"""
import pytest
from pathlib import Path
from typer.testing import CliRunner
from llmhub.cli import app
from llmhub_cli.spec_models import load_spec
from llmhub_cli.runtime_io import load_runtime

runner = CliRunner()


def test_cli_help():
    """Test that CLI help works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "LLMHub CLI" in result.stdout


def test_init_command(tmp_path, monkeypatch):
    """Test llmhub init command."""
    # Change to temp directory
    monkeypatch.chdir(tmp_path)
    
    result = runner.invoke(app, ["init"])
    
    # Should succeed
    assert result.exit_code == 0
    
    # Check files created
    assert (tmp_path / "llmhub.spec.yaml").exists()
    assert (tmp_path / ".env.example").exists()
    
    # Verify spec content
    spec = load_spec(tmp_path / "llmhub.spec.yaml")
    assert spec.project == tmp_path.name
    assert spec.env == "dev"
    assert "openai" in spec.providers
    assert "llm.inference" in spec.roles


def test_generate_command(tmp_path, monkeypatch):
    """Test llmhub generate command."""
    monkeypatch.chdir(tmp_path)
    
    # First init
    runner.invoke(app, ["init"])
    
    # Then generate
    result = runner.invoke(app, ["generate", "--force"])
    
    assert result.exit_code == 0
    assert (tmp_path / "llmhub.yaml").exists()
    
    # Verify runtime
    runtime = load_runtime(tmp_path / "llmhub.yaml")
    assert runtime.project == tmp_path.name
    assert "llm.inference" in runtime.roles


def test_spec_show_command(tmp_path, monkeypatch):
    """Test llmhub spec show command."""
    monkeypatch.chdir(tmp_path)
    
    # Init first
    runner.invoke(app, ["init"])
    
    # Show spec
    result = runner.invoke(app, ["spec", "show"])
    
    assert result.exit_code == 0
    assert "llm.inference" in result.stdout


def test_runtime_show_command(tmp_path, monkeypatch):
    """Test llmhub runtime show command."""
    monkeypatch.chdir(tmp_path)
    
    # Init and generate
    runner.invoke(app, ["init"])
    runner.invoke(app, ["generate", "--force"])
    
    # Show runtime
    result = runner.invoke(app, ["runtime", "show"])
    
    assert result.exit_code == 0
    assert "llm.inference" in result.stdout


def test_env_sync_command(tmp_path, monkeypatch):
    """Test llmhub env sync command."""
    monkeypatch.chdir(tmp_path)
    
    # Init first
    runner.invoke(app, ["init"])
    
    # Remove .env.example to test sync
    (tmp_path / ".env.example").unlink()
    
    # Sync
    result = runner.invoke(app, ["env", "sync"])
    
    assert result.exit_code == 0
    assert (tmp_path / ".env.example").exists()
    
    content = (tmp_path / ".env.example").read_text()
    assert "OPENAI_API_KEY=" in content


def test_status_command(tmp_path, monkeypatch):
    """Test llmhub status command."""
    monkeypatch.chdir(tmp_path)
    
    # Init
    runner.invoke(app, ["init"])
    
    # Status
    result = runner.invoke(app, ["status"])
    
    assert result.exit_code == 0
    assert "Spec" in result.stdout


def test_path_command(tmp_path, monkeypatch):
    """Test llmhub path command."""
    monkeypatch.chdir(tmp_path)
    
    result = runner.invoke(app, ["path"])
    
    assert result.exit_code == 0
    assert "Root:" in result.stdout
    assert "llmhub.spec.yaml" in result.stdout


def test_spec_validate_command(tmp_path, monkeypatch):
    """Test llmhub spec validate command."""
    monkeypatch.chdir(tmp_path)
    
    # Init
    runner.invoke(app, ["init"])
    
    # Validate
    result = runner.invoke(app, ["spec", "validate"])
    
    assert result.exit_code == 0
    assert "valid" in result.stdout.lower()


def test_diff_command(tmp_path, monkeypatch):
    """Test llmhub diff command."""
    monkeypatch.chdir(tmp_path)
    
    # Init and generate
    runner.invoke(app, ["init"])
    runner.invoke(app, ["generate", "--force"])
    
    # Diff
    result = runner.invoke(app, ["runtime", "diff"])
    
    assert result.exit_code == 0
    # Should show roles in sync
    assert "llm.inference" in result.stdout
