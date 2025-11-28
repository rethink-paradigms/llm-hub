import typer
from pathlib import Path
from rich.console import Console
from ..context import resolve_context, ContextOverrides
from ..spec_models import (
    SpecConfig, SpecProviderConfig, RoleSpec, RoleKind,
    Preferences, PreferenceLevel, SpecDefaults, load_spec, save_spec, SpecError
)
from ..env_manager import generate_env_example
from ..runtime_io import load_runtime, RuntimeError as RTError
from .. import ux

console = Console()


def setup() -> None:
    """Interactive setup to create llmhub.spec.yaml."""
    context = resolve_context()
    
    # Check if spec already exists
    if context.spec_path.exists():
        if not ux.confirm(f"Spec already exists at {context.spec_path}. Reinitialize?", default=False):
            console.print("[yellow]Setup cancelled.[/yellow]")
            raise typer.Exit()
    
    console.print("\n[bold]LLMHub Setup[/bold]\n")
    
    # Project name and env
    project_name = ux.prompt_text("Project name", default=context.root.name)
    env_name = ux.prompt_text("Environment", default="dev")
    
    # Select providers
    available_providers = ["openai", "anthropic", "gemini", "mistral", "cohere"]
    console.print("\nSelect providers to enable:")
    selected_providers = ux.multi_select_from_list(
        "Which providers do you want to enable?",
        available_providers
    )
    
    if not selected_providers:
        console.print("[yellow]No providers selected. Using OpenAI as default.[/yellow]")
        selected_providers = ["openai"]
    
    # Build providers config
    providers = {}
    for provider in selected_providers:
        env_key_default = f"{provider.upper()}_API_KEY"
        providers[provider] = SpecProviderConfig(
            enabled=True,
            env_key=env_key_default
        )
    
    # Select standard roles to scaffold
    standard_roles = ["llm.preprocess", "llm.inference", "llm.embedding", "llm.tools"]
    console.print("\nSelect standard roles to create:")
    selected_roles = ux.multi_select_from_list(
        "Which roles do you want to scaffold?",
        standard_roles
    )
    
    # Build roles
    roles = {}
    
    for role_name in selected_roles:
        console.print(f"\n[cyan]Configuring {role_name}[/cyan]")
        
        # Determine kind based on role name
        if "embedding" in role_name:
            kind = RoleKind.embedding
            description = "Vector embeddings for retrieval and similarity."
        elif "preprocess" in role_name:
            kind = RoleKind.chat
            description = "Fast, cheap preprocessing model to normalize input."
        elif "tools" in role_name:
            kind = RoleKind.tool
            description = "Model for tool/function calling."
        else:
            kind = RoleKind.chat
            description = "Main reasoning model for answers."
        
        # Ask for preferences
        console.print(f"  Description: {description}")
        cost_pref = ux.select_from_list("Cost preference?", ["low", "medium", "high"])
        latency_pref = ux.select_from_list("Latency preference?", ["low", "medium", "high"])
        quality_pref = ux.select_from_list("Quality preference?", ["low", "medium", "high"])
        
        roles[role_name] = RoleSpec(
            kind=kind,
            description=description,
            preferences=Preferences(
                cost=PreferenceLevel(cost_pref),
                latency=PreferenceLevel(latency_pref),
                quality=PreferenceLevel(quality_pref),
                providers=selected_providers
            )
        )
    
    # Create spec
    spec = SpecConfig(
        project=project_name,
        env=env_name,
        providers=providers,
        roles=roles,
        defaults=SpecDefaults(providers=selected_providers)
    )
    
    # Save spec
    save_spec(context.spec_path, spec)
    console.print(f"\n[green]✓ Spec saved to {context.spec_path}[/green]")
    
    # Generate .env.example
    generate_env_example(spec, context.env_example_path)
    console.print(f"[green]✓ Environment example saved to {context.env_example_path}[/green]")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Set environment variables in .env or export them")
    console.print("  2. Run: llmhub generate")
    console.print("  3. Run: llmhub test\n")


def init() -> None:
    """Non-interactive initialization with minimal defaults."""
    context = resolve_context()
    
    if context.spec_path.exists():
        console.print(f"[yellow]Spec already exists at {context.spec_path}[/yellow]")
        if not ux.confirm("Overwrite?", default=False):
            raise typer.Exit()
    
    # Create minimal spec
    spec = SpecConfig(
        project=context.root.name,
        env="dev",
        providers={
            "openai": SpecProviderConfig(enabled=True, env_key="OPENAI_API_KEY")
        },
        roles={
            "llm.inference": RoleSpec(
                kind=RoleKind.chat,
                description="Main inference model for answering questions and reasoning.",
                preferences=Preferences(
                    cost=PreferenceLevel.medium,
                    latency=PreferenceLevel.medium,
                    quality=PreferenceLevel.high,
                    providers=["openai"]
                )
            )
        },
        defaults=SpecDefaults(providers=["openai"])
    )
    
    save_spec(context.spec_path, spec)
    console.print(f"[green]✓ Minimal spec created at {context.spec_path}[/green]")
    
    generate_env_example(spec, context.env_example_path)
    console.print(f"[green]✓ Environment example created at {context.env_example_path}[/green]")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Edit llmhub.spec.yaml to add more roles")
    console.print("  2. Set OPENAI_API_KEY environment variable")
    console.print("  3. Run: llmhub generate\n")


def status() -> None:
    """Show project status."""
    context = resolve_context()
    
    spec_exists = context.spec_path.exists()
    runtime_exists = context.runtime_path.exists()
    env_example_exists = context.env_example_path.exists()
    
    issues = []
    
    # Try to load and validate spec
    if spec_exists:
        try:
            spec = load_spec(context.spec_path)
            console.print(f"\n[green]✓ Spec valid ({len(spec.roles)} roles, {len(spec.providers)} providers)[/green]")
        except SpecError as e:
            issues.append(f"Spec validation failed: {e}")
    else:
        issues.append("No spec file found. Run 'llmhub init' or 'llmhub setup'")
    
    # Try to load runtime
    if runtime_exists:
        try:
            runtime = load_runtime(context.runtime_path)
            console.print(f"[green]✓ Runtime valid ({len(runtime.roles)} roles)[/green]")
        except RTError as e:
            issues.append(f"Runtime validation failed: {e}")
    else:
        if spec_exists:
            issues.append("No runtime file. Run 'llmhub generate'")
    
    ux.print_status(context, spec_exists, runtime_exists, env_example_exists, issues)


def path() -> None:
    """Show resolved paths."""
    context = resolve_context()
    
    console.print("\n[bold]Resolved Paths:[/bold]\n")
    console.print(f"Root:        {context.root}")
    console.print(f"Spec:        {context.spec_path}")
    console.print(f"Runtime:     {context.runtime_path}")
    console.print(f"Env example: {context.env_example_path}\n")


def print_status_summary() -> None:
    """Print status summary for default command."""
    try:
        status()
    except Exception:
        console.print("[yellow]Run 'llmhub init' or 'llmhub setup' to get started[/yellow]")
