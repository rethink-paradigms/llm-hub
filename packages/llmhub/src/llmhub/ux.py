from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from llmhub_runtime.models import RuntimeConfig
from .spec_models import SpecConfig
from .env_manager import MissingEnvVar
from .context import ProjectContext


console = Console()


def print_status(
    context: ProjectContext,
    spec_exists: bool,
    runtime_exists: bool,
    env_example_exists: bool,
    issues: Optional[list[str]] = None
) -> None:
    """Print project status summary."""
    console.print("\n[bold]LLMHub Project Status[/bold]\n")
    console.print(f"Root: {context.root}")
    console.print(f"Spec: {context.spec_path} {'✓' if spec_exists else '✗'}")
    console.print(f"Runtime: {context.runtime_path} {'✓' if runtime_exists else '✗'}")
    console.print(f"Env example: {context.env_example_path} {'✓' if env_example_exists else '✗'}")
    
    if issues:
        console.print("\n[yellow]Issues:[/yellow]")
        for issue in issues:
            console.print(f"  • {issue}")


def print_roles_table(spec: SpecConfig) -> None:
    """Pretty-print spec roles in a table."""
    table = Table(title=f"Roles in {spec.project}")
    table.add_column("Role Name", style="cyan")
    table.add_column("Kind", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Preferences", style="green")
    
    for role_name, role_spec in spec.roles.items():
        prefs = []
        if role_spec.preferences.cost:
            prefs.append(f"cost:{role_spec.preferences.cost}")
        if role_spec.preferences.latency:
            prefs.append(f"latency:{role_spec.preferences.latency}")
        if role_spec.preferences.quality:
            prefs.append(f"quality:{role_spec.preferences.quality}")
        
        table.add_row(
            role_name,
            role_spec.kind,
            role_spec.description[:50] + "..." if len(role_spec.description) > 50 else role_spec.description,
            ", ".join(prefs) if prefs else "-"
        )
    
    console.print(table)


def print_runtime_roles(runtime: RuntimeConfig) -> None:
    """Pretty-print runtime roles in a table."""
    table = Table(title=f"Runtime Configuration: {runtime.project}")
    table.add_column("Role Name", style="cyan")
    table.add_column("Provider", style="yellow")
    table.add_column("Model", style="green")
    table.add_column("Mode", style="magenta")
    
    for role_name, role_config in runtime.roles.items():
        table.add_row(
            role_name,
            role_config.provider,
            role_config.model,
            role_config.mode
        )
    
    console.print(table)


def print_providers_table(spec: SpecConfig) -> None:
    """Pretty-print providers in a table."""
    table = Table(title="Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Enabled", style="green")
    table.add_column("Env Key", style="yellow")
    
    for provider_name, provider_config in spec.providers.items():
        table.add_row(
            provider_name,
            "✓" if provider_config.enabled else "✗",
            provider_config.env_key or "-"
        )
    
    console.print(table)


def print_env_check_results(missing: list[MissingEnvVar]) -> None:
    """Print missing environment variables."""
    if not missing:
        console.print("\n[green]✓ All required environment variables are set[/green]\n")
    else:
        console.print(f"\n[red]✗ Missing {len(missing)} environment variable(s):[/red]\n")
        for mv in missing:
            console.print(f"  • {mv.env_key} (for {mv.provider})")
        console.print()


def confirm(prompt: str, default: bool = True) -> bool:
    """Prompt user for yes/no confirmation."""
    return typer.confirm(prompt, default=default)


def prompt_text(prompt: str, default: Optional[str] = None) -> str:
    """Prompt user for text input."""
    if default:
        result = typer.prompt(prompt, default=default)
    else:
        result = typer.prompt(prompt)
    return result


def select_from_list(prompt: str, options: list[str]) -> str:
    """
    Let user select one option from a list.
    For simplicity, just print options and ask for input.
    """
    console.print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        console.print(f"  {i}. {option}")
    
    while True:
        choice = typer.prompt("Enter number", type=int)
        if 1 <= choice <= len(options):
            return options[choice - 1]
        console.print(f"[red]Invalid choice. Please enter 1-{len(options)}[/red]")


def multi_select_from_list(prompt: str, options: list[str]) -> list[str]:
    """
    Let user select multiple options from a list.
    For simplicity, ask for comma-separated numbers.
    """
    console.print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        console.print(f"  {i}. {option}")
    
    console.print("\nEnter numbers separated by commas (e.g., 1,3,4) or 'all':")
    choice = typer.prompt("Selection")
    
    if choice.lower() == 'all':
        return options
    
    try:
        indices = [int(x.strip()) for x in choice.split(',')]
        selected = [options[i - 1] for i in indices if 1 <= i <= len(options)]
        return selected
    except (ValueError, IndexError):
        console.print("[red]Invalid selection, returning empty list[/red]")
        return []
