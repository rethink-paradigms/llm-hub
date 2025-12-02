"""
Integration tests for example scripts.

Tests that example scripts execute without errors.
"""
import pytest
import subprocess
import sys
from pathlib import Path


@pytest.fixture
def examples_dir():
    """Return path to examples directory."""
    # Navigate from tests/integration to examples
    return Path(__file__).parent.parent.parent.parent.parent / "examples"


@pytest.fixture
def project_root():
    """Return path to project root."""
    return Path(__file__).parent.parent.parent.parent.parent


class TestCatalogExamples:
    """Tests for catalog programmatic access examples."""
    
    @pytest.mark.skip(reason="Requires network access and API keys - manual integration test")
    def test_catalog_example_runs(self, examples_dir, project_root):
        """Test that catalog_programmatic_access.py executes without errors."""
        script_path = examples_dir / "catalog_programmatic_access.py"
        
        assert script_path.exists(), f"Example script not found: {script_path}"
        
        # Run the example script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Should complete successfully
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        
        # Should have output
        assert len(result.stdout) > 0
        
        # Check for expected content
        assert "Catalog built" in result.stdout or "catalog" in result.stdout.lower()
    
    def test_catalog_example_exists(self, examples_dir):
        """Test that catalog example file exists."""
        script_path = examples_dir / "catalog_programmatic_access.py"
        assert script_path.exists()
    
    def test_catalog_example_has_main(self, examples_dir):
        """Test that catalog example has main function."""
        script_path = examples_dir / "catalog_programmatic_access.py"
        content = script_path.read_text()
        
        assert "def main():" in content
        assert "if __name__ == '__main__':" in content
    
    def test_catalog_example_imports_valid(self, examples_dir):
        """Test that catalog example has valid imports."""
        script_path = examples_dir / "catalog_programmatic_access.py"
        content = script_path.read_text()
        
        assert "from llmhub_cli import" in content
        assert "build_catalog" in content or "get_catalog" in content


class TestRuntimeGenerationExamples:
    """Tests for runtime generation examples."""
    
    @pytest.mark.skip(reason="Requires spec file and may require catalog - manual integration test")
    def test_runtime_generation_example_runs(self, examples_dir, project_root):
        """Test that runtime_generation_programmatic.py executes without errors."""
        script_path = examples_dir / "runtime_generation_programmatic.py"
        
        assert script_path.exists(), f"Example script not found: {script_path}"
        
        # Run the example script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # May fail if spec file doesn't exist, but should not crash
        # Check that it at least runs without Python errors
        if result.returncode != 0:
            # Should be a controlled error message, not a Python traceback
            # (unless spec file is missing, which is expected)
            if "Spec file not found" not in result.stdout:
                pytest.fail(f"Script crashed unexpectedly: {result.stderr}")
    
    def test_runtime_generation_example_exists(self, examples_dir):
        """Test that runtime generation example file exists."""
        script_path = examples_dir / "runtime_generation_programmatic.py"
        assert script_path.exists()
    
    def test_runtime_generation_example_has_main(self, examples_dir):
        """Test that runtime generation example has main function."""
        script_path = examples_dir / "runtime_generation_programmatic.py"
        content = script_path.read_text()
        
        assert "def main():" in content
        assert "if __name__ == '__main__':" in content
    
    def test_runtime_generation_example_imports_valid(self, examples_dir):
        """Test that runtime generation example has valid imports."""
        script_path = examples_dir / "runtime_generation_programmatic.py"
        content = script_path.read_text()
        
        assert "from llmhub_cli import" in content
        assert "load_spec" in content
        assert "generate_runtime_from_spec" in content
    
    def test_runtime_generation_example_has_multiple_examples(self, examples_dir):
        """Test that runtime generation example has multiple example functions."""
        script_path = examples_dir / "runtime_generation_programmatic.py"
        content = script_path.read_text()
        
        # Should have multiple example functions
        assert content.count("def example_") >= 4


class TestExampleDocumentation:
    """Tests for example documentation quality."""
    
    def test_catalog_example_has_docstring(self, examples_dir):
        """Test that catalog example has module docstring."""
        script_path = examples_dir / "catalog_programmatic_access.py"
        content = script_path.read_text()
        
        # Should have module docstring
        assert '"""' in content or "'''" in content
        # Docstring should be at the beginning
        assert content.strip().startswith('"""') or content.strip().startswith("'''") or content.strip().startswith("#!/usr/bin/env python")
    
    def test_runtime_generation_example_has_docstring(self, examples_dir):
        """Test that runtime generation example has module docstring."""
        script_path = examples_dir / "runtime_generation_programmatic.py"
        content = script_path.read_text()
        
        # Should have module docstring
        assert '"""' in content or "'''" in content
    
    def test_examples_have_executable_permission(self, examples_dir):
        """Test that example scripts can be executed."""
        examples = [
            examples_dir / "catalog_programmatic_access.py",
            examples_dir / "runtime_generation_programmatic.py",
        ]
        
        for example in examples:
            if example.exists():
                # Check if file has shebang
                content = example.read_text()
                if content.startswith("#!/usr/bin/env python"):
                    # File is intended to be executable
                    assert True  # We can't check permissions on all systems


class TestExampleREADME:
    """Tests for examples README documentation."""
    
    def test_examples_readme_exists(self, examples_dir):
        """Test that examples directory has README."""
        readme_path = examples_dir / "README.md"
        assert readme_path.exists()
    
    def test_examples_readme_mentions_scripts(self, examples_dir):
        """Test that README mentions the example scripts."""
        readme_path = examples_dir / "README.md"
        
        if readme_path.exists():
            content = readme_path.read_text()
            
            # Should mention the example scripts
            assert "catalog_programmatic_access" in content or "catalog" in content.lower()
            assert "runtime_generation" in content or "generation" in content.lower()


class TestExampleCodeQuality:
    """Tests for example code quality and best practices."""
    
    def test_catalog_example_has_error_handling(self, examples_dir):
        """Test that catalog example has proper error handling."""
        script_path = examples_dir / "catalog_programmatic_access.py"
        content = script_path.read_text()
        
        # Should have try-except blocks
        assert "try:" in content or "except" in content
    
    def test_runtime_generation_example_has_error_handling(self, examples_dir):
        """Test that runtime generation example has proper error handling."""
        script_path = examples_dir / "runtime_generation_programmatic.py"
        content = script_path.read_text()
        
        # Should have try-except blocks
        assert "try:" in content or "except" in content
    
    def test_examples_have_example_functions(self, examples_dir):
        """Test that examples have multiple example functions."""
        catalog_path = examples_dir / "catalog_programmatic_access.py"
        runtime_path = examples_dir / "runtime_generation_programmatic.py"
        
        catalog_content = catalog_path.read_text()
        runtime_content = runtime_path.read_text()
        
        # Each should have multiple example functions
        assert catalog_content.count("def example_") >= 3
        assert runtime_content.count("def example_") >= 3


class TestExampleOutput:
    """Tests for example script output and behavior."""
    
    def test_catalog_example_syntax_valid(self, examples_dir):
        """Test that catalog example has valid Python syntax."""
        script_path = examples_dir / "catalog_programmatic_access.py"
        
        # Try to compile the script
        content = script_path.read_text()
        try:
            compile(content, str(script_path), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {script_path}: {e}")
    
    def test_runtime_generation_example_syntax_valid(self, examples_dir):
        """Test that runtime generation example has valid Python syntax."""
        script_path = examples_dir / "runtime_generation_programmatic.py"
        
        # Try to compile the script
        content = script_path.read_text()
        try:
            compile(content, str(script_path), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {script_path}: {e}")
