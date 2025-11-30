import typer
from rich.console import Console
from ..context import resolve_context
from ..spec_models import (
    load_spec, save_spec, SpecError, RoleSpec, RoleKind,
    Preferences, PreferenceLevel
)
from .. import ux

console = Console()


def spec_show() -> None:
    """Show spec configuration."""
    context = resolve_context()
    
    if not context.spec_path.exists():
        console.print(f"[red]No spec file found at {context.spec_path}[/red]")
        console.print("Run 'llmhub init' or 'llmhub setup' first")
        raise typer.Exit(1)
    
    try:
        spec = load_spec(context.spec_path)
        console.print(f"\n[bold]Project:[/bold] {spec.project}")
        console.print(f"[bold]Environment:[/bold] {spec.env}\n")
        
        ux.print_providers_table(spec)
        console.print()
        ux.print_roles_table(spec)
        
    except SpecError as e:
        console.print(f"[red]Error loading spec: {e}[/red]")
        raise typer.Exit(1)


def spec_validate() -> None:
    """Validate spec file."""
    context = resolve_context()
    
    if not context.spec_path.exists():
        console.print(f"[red]No spec file found at {context.spec_path}[/red]")
        raise typer.Exit(1)
    
    try:
        spec = load_spec(context.spec_path)
        console.print("[green]✓ Spec is valid[/green]")
        console.print(f"  Project: {spec.project}")
        console.print(f"  Roles: {len(spec.roles)}")
        console.print(f"  Providers: {len(spec.providers)}")
    except SpecError as e:
        console.print(f"[red]✗ Spec validation failed:[/red]")
        console.print(f"  {e}")
        raise typer.Exit(1)


def roles() -> None:
    """List all roles."""
    context = resolve_context()
    
    if not context.spec_path.exists():
        console.print(f"[red]No spec file found at {context.spec_path}[/red]")
        raise typer.Exit(1)
    
    try:
        spec = load_spec(context.spec_path)
        ux.print_roles_table(spec)
    except SpecError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def add_role(name: str) -> None:
    """Add a new role to spec."""
    context = resolve_context()
    
    if not context.spec_path.exists():
        console.print(f"[red]No spec file found at {context.spec_path}[/red]")
        console.print("Run 'llmhub init' first")
        raise typer.Exit(1)
    
    try:
        spec = load_spec(context.spec_path)
        
        # Check if role already exists
        if name in spec.roles:
            console.print(f"[yellow]Role '{name}' already exists[/yellow]")
            if ux.confirm("Edit it instead?", default=True):
                edit_role(name)
                return
            else:
                raise typer.Exit()
        
        console.print(f"\n[bold]Adding role: {name}[/bold]\n")
        
        # Select kind
        kind_str = ux.select_from_list(
            "Select role kind:",
            ["chat", "embedding", "image", "audio", "tool", "other"]
        )
        kind = RoleKind(kind_str)
        
        # Get description
        description = ux.prompt_text("Description")
        
        # Get preferences
        console.print("\n[bold]Preferences:[/bold]")
        cost = ux.select_from_list("Cost preference:", ["low", "medium", "high"])
        latency = ux.select_from_list("Latency preference:", ["low", "medium", "high"])
        quality = ux.select_from_list("Quality preference:", ["low", "medium", "high"])
        
        # Select providers
        enabled_providers = [p for p, cfg in spec.providers.items() if cfg.enabled]
        if enabled_providers:
            console.print("\n[bold]Providers:[/bold]")
            selected_providers = ux.multi_select_from_list(
                "Select preferred providers:",
                enabled_providers
            )
        else:
            selected_providers = []
        
        # Create role
        role = RoleSpec(
            kind=kind,
            description=description,
            preferences=Preferences(
                cost=PreferenceLevel(cost),
                latency=PreferenceLevel(latency),
                quality=PreferenceLevel(quality),
                providers=selected_providers if selected_providers else None
            )
        )
        
        spec.roles[name] = role
        save_spec(context.spec_path, spec)
        
        console.print(f"\n[green]✓ Role '{name}' added to spec[/green]")
        console.print("Run 'llmhub generate' to update runtime")
        
    except SpecError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def edit_role(name: str) -> None:
    """Edit an existing role."""
    context = resolve_context()
    
    if not context.spec_path.exists():
        console.print(f"[red]No spec file found at {context.spec_path}[/red]")
        raise typer.Exit(1)
    
    try:
        spec = load_spec(context.spec_path)
        
        if name not in spec.roles:
            console.print(f"[red]Role '{name}' not found[/red]")
            raise typer.Exit(1)
        
        role = spec.roles[name]
        console.print(f"\n[bold]Editing role: {name}[/bold]")
        console.print(f"Current kind: {role.kind}")
        console.print(f"Current description: {role.description}\n")
        
        if ux.confirm("Edit description?", default=False):
            role.description = ux.prompt_text("New description", default=role.description)
        
        if ux.confirm("Edit preferences?", default=True):
            cost = ux.select_from_list(
                "Cost preference:",
                ["low", "medium", "high"]
            )
            latency = ux.select_from_list(
                "Latency preference:",
                ["low", "medium", "high"]
            )
            quality = ux.select_from_list(
                "Quality preference:",
                ["low", "medium", "high"]
            )
            
            role.preferences.cost = PreferenceLevel(cost)
            role.preferences.latency = PreferenceLevel(latency)
            role.preferences.quality = PreferenceLevel(quality)
        
        save_spec(context.spec_path, spec)
        console.print(f"\n[green]✓ Role '{name}' updated[/green]")
        console.print("Run 'llmhub generate' to update runtime")
        
    except SpecError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def rm_role(name: str) -> None:
    """Remove a role from spec."""
    context = resolve_context()
    
    if not context.spec_path.exists():
        console.print(f"[red]No spec file found at {context.spec_path}[/red]")
        raise typer.Exit(1)
    
    try:
        spec = load_spec(context.spec_path)
        
        if name not in spec.roles:
            console.print(f"[red]Role '{name}' not found[/red]")
            raise typer.Exit(1)
        
        if not ux.confirm(f"Remove role '{name}'?", default=False):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit()
        
        del spec.roles[name]
        save_spec(context.spec_path, spec)
        
        console.print(f"[green]✓ Role '{name}' removed[/green]")
        console.print("Run 'llmhub generate' to update runtime")
        
    except SpecError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
