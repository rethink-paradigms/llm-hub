import typer
from rich.console import Console
from ..context import resolve_context
from ..spec_models import load_spec, SpecError
from ..runtime_io import load_runtime, save_runtime, RuntimeError as RTError
from ..env_manager import generate_env_example
from ..generator_hook import generate_runtime, GeneratorOptions
from .. import ux

console = Console()


def generate(
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be generated without writing"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Use heuristic-only mode"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing runtime without confirmation"),
    explain: bool = typer.Option(False, "--explain", help="Show explanations for model selections")
) -> None:
    """Generate runtime config from spec."""
    context = resolve_context()
    
    if not context.spec_path.exists():
        console.print(f"[red]No spec file found at {context.spec_path}[/red]")
        console.print("Run 'llmhub init' first")
        raise typer.Exit(1)
    
    try:
        # Load spec
        spec = load_spec(context.spec_path)
        console.print(f"[cyan]Loaded spec: {spec.project}[/cyan]")
        
        # Check if runtime exists
        if context.runtime_path.exists() and not force and not dry_run:
            if not ux.confirm(f"Runtime already exists at {context.runtime_path}. Overwrite?", default=True):
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit()
        
        # Generate runtime
        console.print("[cyan]Generating runtime configuration...[/cyan]")
        options = GeneratorOptions(no_llm=no_llm, explain=explain)
        result = generate_runtime(spec, options)
        
        if dry_run:
            console.print("\n[bold]Generated Runtime (dry-run):[/bold]\n")
            ux.print_runtime_roles(result.runtime)
            
            if explain and result.explanations:
                console.print("\n[bold]Explanations:[/bold]\n")
                for role, explanation in result.explanations.items():
                    console.print(f"[cyan]{role}:[/cyan] {explanation}")
        else:
            # Save runtime
            save_runtime(context.runtime_path, result.runtime)
            console.print(f"\n[green]✓ Runtime saved to {context.runtime_path}[/green]")
            
            # Update .env.example if providers changed
            generate_env_example(spec, context.env_example_path, overwrite=True)
            console.print(f"[green]✓ Environment example updated[/green]")
            
            if explain and result.explanations:
                console.print("\n[bold]Model Selections:[/bold]\n")
                for role, explanation in result.explanations.items():
                    console.print(f"[cyan]{role}:[/cyan] {explanation}")
            
            console.print("\n[bold]Next steps:[/bold]")
            console.print("  1. Review the generated llmhub.yaml")
            console.print("  2. Set required environment variables")
            console.print("  3. Run: llmhub test\n")
        
    except SpecError as e:
        console.print(f"[red]Spec error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Generation failed: {e}[/red]")
        raise typer.Exit(1)


def runtime_show() -> None:
    """Show runtime configuration."""
    context = resolve_context()
    
    if not context.runtime_path.exists():
        console.print(f"[red]No runtime file found at {context.runtime_path}[/red]")
        console.print("Run 'llmhub generate' first")
        raise typer.Exit(1)
    
    try:
        runtime = load_runtime(context.runtime_path)
        console.print(f"\n[bold]Project:[/bold] {runtime.project}")
        console.print(f"[bold]Environment:[/bold] {runtime.env}\n")
        
        ux.print_runtime_roles(runtime)
        
    except RTError as e:
        console.print(f"[red]Error loading runtime: {e}[/red]")
        raise typer.Exit(1)


def diff() -> None:
    """Show diff between spec and runtime."""
    context = resolve_context()
    
    if not context.spec_path.exists():
        console.print(f"[red]No spec file found[/red]")
        raise typer.Exit(1)
    
    try:
        spec = load_spec(context.spec_path)
        
        if not context.runtime_path.exists():
            console.print(f"[yellow]No runtime file found[/yellow]")
            console.print(f"\nAll {len(spec.roles)} role(s) from spec need to be generated:")
            for role_name in spec.roles.keys():
                console.print(f"  + {role_name}")
            console.print("\nRun 'llmhub generate' to create runtime")
            return
        
        runtime = load_runtime(context.runtime_path)
        
        spec_roles = set(spec.roles.keys())
        runtime_roles = set(runtime.roles.keys())
        
        only_in_spec = spec_roles - runtime_roles
        only_in_runtime = runtime_roles - spec_roles
        in_both = spec_roles & runtime_roles
        
        console.print("\n[bold]Spec vs Runtime Diff:[/bold]\n")
        
        if only_in_spec:
            console.print(f"[yellow]Roles in spec but not in runtime ({len(only_in_spec)}):[/yellow]")
            for role in sorted(only_in_spec):
                console.print(f"  + {role}")
            console.print()
        
        if only_in_runtime:
            console.print(f"[yellow]Roles in runtime but not in spec ({len(only_in_runtime)}):[/yellow]")
            for role in sorted(only_in_runtime):
                console.print(f"  - {role}")
            console.print()
        
        if in_both:
            console.print(f"[green]Roles in both ({len(in_both)}):[/green]")
            for role in sorted(in_both):
                runtime_role = runtime.roles[role]
                console.print(f"  = {role} → {runtime_role.provider}:{runtime_role.model}")
            console.print()
        
        if only_in_spec or only_in_runtime:
            console.print("[yellow]Run 'llmhub generate' to sync[/yellow]")
        else:
            console.print("[green]✓ Spec and runtime are in sync[/green]")
        
    except (SpecError, RTError) as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
