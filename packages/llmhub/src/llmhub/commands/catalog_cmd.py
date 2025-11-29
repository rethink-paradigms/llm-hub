"""
Catalog CLI commands.

Implements `llmhub catalog show` and `llmhub catalog refresh`.
"""
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from ..catalog import build_catalog


console = Console()


def catalog_refresh(
    ttl_hours: int = typer.Option(24, help="Cache TTL in hours"),
) -> None:
    """
    Force rebuild of the catalog and update cache.
    
    Fetches fresh data from all sources and rebuilds the catalog.
    """
    try:
        console.print("\n[bold]Refreshing catalog...[/bold]\n")
        
        catalog = build_catalog(ttl_hours=ttl_hours, force_refresh=True)
        
        console.print(f"\n[green]✓ Catalog built successfully[/green]")
        console.print(f"  Models: {len(catalog.models)}")
        console.print(f"  Built at: {catalog.built_at}")
        console.print(f"  Version: {catalog.catalog_version}\n")
        
        # Provider summary
        provider_counts = {}
        for model in catalog.models:
            provider_counts[model.provider] = provider_counts.get(model.provider, 0) + 1
        
        if provider_counts:
            console.print("[bold]Models by provider:[/bold]")
            for provider, count in sorted(provider_counts.items()):
                console.print(f"  {provider}: {count}")
        
        console.print()
        
    except Exception as e:
        console.print(f"\n[red]✗ Failed to build catalog: {e}[/red]\n")
        raise typer.Exit(1)


def catalog_show(
    provider: Optional[str] = typer.Option(None, help="Filter by provider"),
    show_details: bool = typer.Option(False, "--details", help="Show detailed model info"),
) -> None:
    """
    Show the current catalog of available models.
    
    Displays a table of models with pricing, quality, and capabilities.
    """
    try:
        console.print("\n[bold]Loading catalog...[/bold]\n")
        
        catalog = build_catalog(force_refresh=False)
        
        if not catalog.models:
            console.print("[yellow]No models found in catalog.[/yellow]")
            console.print("Run 'llmhub catalog refresh' to build the catalog.\n")
            return
        
        # Filter by provider if specified
        models = catalog.models
        if provider:
            models = [m for m in models if m.provider.lower() == provider.lower()]
            if not models:
                console.print(f"[yellow]No models found for provider: {provider}[/yellow]\n")
                return
        
        # Group by provider
        providers = {}
        for model in models:
            if model.provider not in providers:
                providers[model.provider] = []
            providers[model.provider].append(model)
        
        # Print summary
        console.print(f"[bold]Catalog Summary[/bold]")
        console.print(f"  Total models: {len(models)}")
        console.print(f"  Providers: {len(providers)}")
        console.print(f"  Built: {catalog.built_at}\n")
        
        # Print table per provider
        for prov_name in sorted(providers.keys()):
            prov_models = providers[prov_name]
            
            table = Table(title=f"{prov_name} ({len(prov_models)} models)")
            table.add_column("Model", style="cyan")
            table.add_column("Cost Tier", style="green", justify="center")
            table.add_column("Quality Tier", style="yellow", justify="center")
            
            if show_details:
                table.add_column("Arena Score", style="magenta", justify="right")
                table.add_column("Tags", style="blue")
            
            for model in sorted(prov_models, key=lambda m: m.quality_tier):
                row = [
                    model.model_id,
                    str(model.cost_tier),
                    str(model.quality_tier),
                ]
                
                if show_details:
                    arena_str = f"{model.arena_score:.0f}" if model.arena_score else "-"
                    tags_str = ", ".join(model.tags[:3]) if model.tags else "-"
                    row.extend([arena_str, tags_str])
                
                table.add_row(*row)
            
            console.print(table)
            console.print()
        
        # Legend
        console.print("[dim]Tiers: 1=best/cheapest, 5=worst/most expensive[/dim]\n")
        
    except Exception as e:
        console.print(f"\n[red]✗ Failed to load catalog: {e}[/red]\n")
        raise typer.Exit(1)
