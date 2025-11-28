import typer
from pathlib import Path
from rich.console import Console
from ..context import resolve_context
from ..spec_models import load_spec, SpecError
from ..env_manager import generate_env_example, check_env
from .. import ux

console = Console()


def env_sync(
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be written without writing")
) -> None:
    """Sync .env.example from spec."""
    context = resolve_context()
    
    if not context.spec_path.exists():
        console.print(f"[red]No spec file found at {context.spec_path}[/red]")
        console.print("Run 'llmhub init' first")
        raise typer.Exit(1)
    
    try:
        spec = load_spec(context.spec_path)
        
        if dry_run:
            console.print("\n[bold].env.example content (dry-run):[/bold]\n")
            console.print(f"# LLMHub generated .env.example for project: {spec.project} (env: {spec.env})")
            console.print()
            for provider_name, provider_config in spec.providers.items():
                if provider_config.env_key:
                    console.print(f"# {provider_name.capitalize()} API key")
                    console.print(f"{provider_config.env_key}=")
                    console.print()
        else:
            generate_env_example(spec, context.env_example_path, overwrite=True)
            console.print(f"[green]✓ Environment example synced to {context.env_example_path}[/green]")
        
    except SpecError as e:
        console.print(f"[red]Spec error: {e}[/red]")
        raise typer.Exit(1)


def env_check(
    env_file: str = typer.Option(None, "--env-file", help="Path to .env file to load")
) -> None:
    """Check for missing environment variables."""
    context = resolve_context()
    
    if not context.spec_path.exists():
        console.print(f"[red]No spec file found at {context.spec_path}[/red]")
        raise typer.Exit(1)
    
    try:
        spec = load_spec(context.spec_path)
        
        # Load .env file if specified
        dotenv_path = None
        if env_file:
            dotenv_path = Path(env_file)
        else:
            # Try to find .env in project root
            default_env = context.root / ".env"
            if default_env.exists():
                dotenv_path = default_env
        
        missing = check_env(spec, dotenv_path)
        
        if dotenv_path:
            console.print(f"[cyan]Loaded environment from {dotenv_path}[/cyan]")
        
        ux.print_env_check_results(missing)
        
        if missing:
            console.print("[yellow]Set missing variables in .env or export them[/yellow]")
            raise typer.Exit(1)
        
    except SpecError as e:
        console.print(f"[red]Spec error: {e}[/red]")
        raise typer.Exit(1)
