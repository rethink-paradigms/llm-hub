#!/usr/bin/env python3
"""
LLM Hub Release Script

Automates the PyPI release process:
1. Version bumping (patch, minor, major)
2. Building distribution packages
3. Verification and validation
4. PyPI upload with authentication

Usage:
    python scripts/release.py patch   # 0.1.0 -> 0.1.1
    python scripts/release.py minor   # 0.1.0 -> 0.2.0
    python scripts/release.py major   # 0.1.0 -> 1.0.0
    python scripts/release.py --version 0.2.0  # Specific version
    
    # Release individual packages:
    python scripts/release.py patch --package llmhub-runtime
    python scripts/release.py minor --package llmhub
"""
import sys
import os
import re
import subprocess
import shutil
import getpass
from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(msg: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_step(msg: str):
    """Print step message"""
    print(f"{Colors.CYAN}▶ {msg}{Colors.END}")


def print_success(msg: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_warning(msg: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def print_error(msg: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def run_command(cmd: list, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run shell command with optional output capture"""
    print(f"  $ {' '.join(cmd)}")
    if capture:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)
    else:
        return subprocess.run(cmd, check=check)


def get_workspace_root() -> Path:
    """Get repository root directory"""
    return Path(__file__).parent.parent.absolute()


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse semantic version string"""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)"""
    major, minor, patch = parse_version(current)
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def get_current_version(pyproject_path: Path) -> str:
    """Extract current version from pyproject.toml"""
    content = pyproject_path.read_text()
    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        raise ValueError(f"Version not found in {pyproject_path}")
    return match.group(1)


def update_version_in_file(file_path: Path, old_version: str, new_version: str):
    """Update version in a file"""
    content = file_path.read_text()
    
    # Update version = "x.y.z" pattern
    content = re.sub(
        r'^version\s*=\s*["\']' + re.escape(old_version) + r'["\']',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    
    # Update dependency version patterns (e.g., rethink-llmhub-runtime>=0.1.0)
    content = re.sub(
        r'rethink-llmhub-runtime>=' + re.escape(old_version),
        f'rethink-llmhub-runtime>={new_version}',
        content
    )
    
    file_path.write_text(content)


def clean_build_artifacts(package_dir: Path):
    """Remove build artifacts"""
    artifacts = ['build', 'dist', '*.egg-info']
    for pattern in artifacts:
        if '*' in pattern:
            for path in package_dir.glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
        else:
            path = package_dir / pattern
            if path.exists():
                shutil.rmtree(path)


def build_package(package_dir: Path) -> bool:
    """Build distribution packages"""
    print_step(f"Building {package_dir.name}...")
    
    # Clean old artifacts
    clean_build_artifacts(package_dir)
    
    # Build using python -m build
    try:
        result = run_command(
            [sys.executable, '-m', 'build', str(package_dir)],
            capture=True
        )
        print_success(f"Built {package_dir.name}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Build failed for {package_dir.name}")
        print(e.stderr)
        return False


def verify_package(dist_dir: Path) -> bool:
    """Verify package integrity using twine"""
    print_step(f"Verifying packages in {dist_dir}...")
    
    try:
        result = run_command(
            [sys.executable, '-m', 'twine', 'check', f'{dist_dir}/*'],
            capture=True
        )
        print_success("Package verification passed")
        return True
    except subprocess.CalledProcessError as e:
        print_error("Package verification failed")
        print(e.stderr)
        return False


def confirm(prompt: str) -> bool:
    """Ask user for confirmation"""
    response = input(f"{Colors.YELLOW}{prompt} (y/N): {Colors.END}").strip().lower()
    return response in ['y', 'yes']


def get_pypi_token(test_pypi: bool = False) -> Optional[str]:
    """Get PyPI API token from .env or prompt user"""
    env_var = "PYPI_TEST_API_TOKEN" if test_pypi else "PYPI_API_TOKEN"
    repo_name = "TestPyPI" if test_pypi else "PyPI"
    
    # Try to get from environment (loaded from .env)
    token = os.getenv(env_var)
    
    if token:
        print_success(f"Using {env_var} from .env file")
        return token
    
    # Fallback to manual input
    print(f"\n{Colors.BOLD}Authentication Required{Colors.END}")
    print(f"{env_var} not found in .env file")
    print(f"Please provide your {repo_name} API token")
    print(f"(Create one at: https://{'test.' if test_pypi else ''}pypi.org/manage/account/token/)\n")
    
    token = getpass.getpass(f"{repo_name} API Token: ")
    if not token:
        print_error("No token provided")
        return None
    
    return token


def upload_to_pypi(package_name: str, dist_dir: Path, test_pypi: bool = False):
    """Upload package to PyPI with authentication"""
    repo_name = "TestPyPI" if test_pypi else "PyPI"
    repo_url = "https://test.pypi.org/legacy/" if test_pypi else "https://upload.pypi.org/legacy/"
    
    print_header(f"Upload {package_name} to {repo_name}")
    
    # List files to upload
    files = list(dist_dir.glob("*"))
    if not files:
        print_error(f"No distribution files found in {dist_dir}")
        return False
    
    print(f"\n{Colors.BOLD}Files to upload:{Colors.END}")
    for f in files:
        print(f"  • {f.name}")
    print()
    
    # Confirm upload
    if not confirm(f"Upload {package_name} to {repo_name}?"):
        print_warning("Upload cancelled")
        return False
    
    # Get API token
    token = get_pypi_token(test_pypi)
    if not token:
        return False
    
    # Upload using twine
    print_step(f"Uploading to {repo_name}...")
    
    try:
        cmd = [
            sys.executable, '-m', 'twine', 'upload',
            '--repository-url', repo_url,
            '--username', '__token__',
            '--password', token,
            f'{dist_dir}/*'
        ]
        
        # Run without printing password
        print(f"  $ {' '.join(cmd[:-2])} --password <REDACTED> {cmd[-1]}")
        result = subprocess.run(cmd, check=True)
        
        print_success(f"Successfully uploaded {package_name} to {repo_name}!")
        print(f"\n{Colors.GREEN}Package URL: https://{'test.' if test_pypi else ''}pypi.org/project/{package_name}/{Colors.END}\n")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Upload failed")
        return False


def check_dependencies():
    """Check required dependencies are installed"""
    print_step("Checking dependencies...")
    
    required = ['build', 'twine']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print_error(f"Missing required packages: {', '.join(missing)}")
        print(f"\nInstall with: {Colors.CYAN}pip install {' '.join(missing)}{Colors.END}\n")
        sys.exit(1)
    
    print_success("All dependencies installed")


def parse_arguments():
    """Parse command line arguments"""
    args = {
        'bump_type': None,
        'version': None,
        'package': None  # 'llmhub-runtime', 'llmhub', or None for both
    }
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--version':
            if i + 1 >= len(sys.argv):
                print_error("--version requires a version argument")
                sys.exit(1)
            args['version'] = sys.argv[i + 1]
            i += 2
        elif arg == '--package':
            if i + 1 >= len(sys.argv):
                print_error("--package requires a package name (llmhub-runtime or llmhub)")
                sys.exit(1)
            package = sys.argv[i + 1]
            if package not in ['rethink-llmhub-runtime', 'rethink-llmhub']:
                print_error(f"Invalid package: {package}. Use 'rethink-llmhub-runtime' or 'rethink-llmhub'")
                sys.exit(1)
            args['package'] = package
            i += 2
        elif arg in ['major', 'minor', 'patch']:
            args['bump_type'] = arg
            i += 1
        else:
            print_error(f"Invalid argument: {arg}")
            sys.exit(1)
    
    return args


def main():
    """Main release workflow"""
    workspace = get_workspace_root()
    
    print_header("LLM Hub PyPI Release")
    
    # Load .env file if it exists
    env_file = workspace / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print_success(f"Loaded environment from {env_file}")
    else:
        print_warning("No .env file found. Will prompt for PyPI token if needed.")
    
    # Parse arguments
    if len(sys.argv) < 2:
        print_error("Usage: python scripts/release.py <patch|minor|major|--version X.Y.Z> [--package PKG]")
        print("\nExamples:")
        print("  python scripts/release.py patch     # 0.1.0 -> 0.1.1 (both packages)")
        print("  python scripts/release.py minor     # 0.1.0 -> 0.2.0 (both packages)")
        print("  python scripts/release.py major     # 0.1.0 -> 1.0.0 (both packages)")
        print("  python scripts/release.py --version 0.2.0")
        print("  python scripts/release.py patch --package rethink-llmhub-runtime  # Single package")
        print("  python scripts/release.py minor --package rethink-llmhub          # Single package")
        sys.exit(1)
    
    args = parse_arguments()
    
    # Check dependencies
    check_dependencies()
    
    # Determine which packages to release
    runtime_pyproject = workspace / 'packages/runtime/pyproject.toml'
    llmhub_pyproject = workspace / 'packages/cli/pyproject.toml'
    
    release_runtime = args['package'] is None or args['package'] == 'rethink-llmhub-runtime'
    release_llmhub = args['package'] is None or args['package'] == 'rethink-llmhub'
    
    runtime_current = get_current_version(runtime_pyproject) if release_runtime else None
    llmhub_current = get_current_version(llmhub_pyproject) if release_llmhub else None
    
    # Determine new version
    if args['version']:
        new_version = args['version']
        # Validate version format
        parse_version(new_version)
    elif args['bump_type']:
        # Use the higher current version as base, or the single package version
        if release_runtime and release_llmhub:
            base_version = max(runtime_current, llmhub_current, key=lambda v: parse_version(v))
        elif release_runtime:
            base_version = runtime_current
        else:
            base_version = llmhub_current
        new_version = bump_version(base_version, args['bump_type'])
    else:
        print_error("Must specify version bump type or --version")
        sys.exit(1)
    
    print(f"\n{Colors.BOLD}Version Update:{Colors.END}")
    if release_runtime:
        print(f"  rethink-llmhub-runtime: {runtime_current} → {new_version}")
    if release_llmhub:
        print(f"  rethink-llmhub:         {llmhub_current} → {new_version}")
    print()
    
    if not confirm("Proceed with version bump?"):
        print_warning("Release cancelled")
        sys.exit(0)
    
    # Update versions
    print_header("Step 1: Version Bump")
    
    if release_runtime:
        print_step("Updating rethink-llmhub-runtime version...")
        update_version_in_file(runtime_pyproject, runtime_current, new_version)
        print_success(f"Updated {runtime_pyproject.name}")
    
    if release_llmhub:
        print_step("Updating rethink-llmhub version...")
        update_version_in_file(llmhub_pyproject, llmhub_current, new_version)
        print_success(f"Updated {llmhub_pyproject.name}")
    
    # Build packages
    print_header("Step 2: Build Distribution Packages")
    
    runtime_dir = workspace / 'packages/runtime'
    llmhub_dir = workspace / 'packages/cli'
    runtime_dist = runtime_dir / 'dist'
    llmhub_dist = llmhub_dir / 'dist'
    
    if release_runtime:
        if not build_package(runtime_dir):
            sys.exit(1)
    
    if release_llmhub:
        if not build_package(llmhub_dir):
            sys.exit(1)
    
    # Verify packages
    print_header("Step 3: Verify Package Integrity")
    
    if release_runtime:
        if not verify_package(runtime_dist):
            sys.exit(1)
    
    if release_llmhub:
        if not verify_package(llmhub_dist):
            sys.exit(1)
    
    # Show package contents
    print(f"\n{Colors.BOLD}Distribution Packages:{Colors.END}")
    
    if release_runtime:
        print(f"\n{Colors.CYAN}rethink-llmhub-runtime:{Colors.END}")
        for f in sorted(runtime_dist.glob("*")):
            print(f"  • {f.name}")
    
    if release_llmhub:
        print(f"\n{Colors.CYAN}rethink-llmhub:{Colors.END}")
        for f in sorted(llmhub_dist.glob("*")):
            print(f"  • {f.name}")
    print()
    
    # Upload to PyPI
    print_header("Step 4: Upload to PyPI")
    
    # Ask if testing on TestPyPI first
    test_first = confirm("Upload to TestPyPI first (recommended)?")
    
    if test_first:
        # Upload to TestPyPI
        if release_runtime:
            if not upload_to_pypi("rethink-llmhub-runtime", runtime_dist, test_pypi=True):
                sys.exit(1)
        
        if release_llmhub:
            if not upload_to_pypi("rethink-llmhub", llmhub_dist, test_pypi=True):
                sys.exit(1)
        
        print_success("TestPyPI upload complete!")
        print(f"\nTest installation with:")
        if release_runtime and release_llmhub:
            print(f"{Colors.CYAN}pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ rethink-llmhub=={new_version}{Colors.END}\n")
        elif release_runtime:
            print(f"{Colors.CYAN}pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ rethink-llmhub-runtime=={new_version}{Colors.END}\n")
        else:
            print(f"{Colors.CYAN}pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ rethink-llmhub=={new_version}{Colors.END}\n")
        
        if not confirm("Proceed with production PyPI upload?"):
            print_warning("Production upload cancelled")
            sys.exit(0)
    
    # Upload to production PyPI
    if release_runtime:
        if not upload_to_pypi("rethink-llmhub-runtime", runtime_dist, test_pypi=False):
            sys.exit(1)
    
    if release_llmhub:
        if not upload_to_pypi("rethink-llmhub", llmhub_dist, test_pypi=False):
            sys.exit(1)
    
    # Success!
    print_header("Release Complete! 🎉")
    
    print(f"{Colors.GREEN}Successfully released version {new_version} to PyPI!{Colors.END}\n")
    print(f"Installation command:")
    print(f"{Colors.CYAN}pip install rethink-llmhub=={new_version}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Next steps:{Colors.END}")
    print(f"  1. Commit version changes: git add packages/*/pyproject.toml")
    print(f"  2. Create release tag: git tag v{new_version}")
    print(f"  3. Push changes: git push && git push --tags")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Release cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
