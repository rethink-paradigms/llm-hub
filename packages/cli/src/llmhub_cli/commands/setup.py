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
    
    # Write concise spec guide
    guide_path = context.root / "SPEC_GUIDE.md"
    
    # Get version from package
    from llmhub_cli import __version__
    
    guide_content = (
        "# LLMHub Spec Guide\n\n"
        f"> Generated by LLMHub v{__version__}  \n"
        "> For AI Agents: Full capability documentation at [llmhub.aimanifest.yaml](https://github.com/rethink-paradigms/llm-hub/blob/main/llmhub.aimanifest.yaml)\n\n"
        "This short guide explains the shape of `llmhub.spec.yaml`. Keep it simple — add what you need and grow later.\n\n"
        "## Required sections\n"
        "- **project**: A short name for your app (text).\n"
        "- **env**: Your environment label (e.g., `dev`, `prod`).\n"
        "- **providers**: Available AI providers with an API key mapping.\n"
        "- **roles**: Named roles your app uses (e.g., `llm.inference`).\n\n"
        "## Providers\n"
        "Each provider entry looks like this:\n\n"
        "```yaml\n"
        "providers:\n"
        "  openai:\n"
        "    enabled: true\n"
        "    env_key: OPENAI_API_KEY\n"
        "  anthropic:\n"
        "    enabled: true\n"
        "    env_key: ANTHROPIC_API_KEY\n"
        "```\n"
        "- **enabled**: Set `true` to allow selection.\n"
        "- **env_key**: Name of the environment variable that holds the API key.\n\n"
        "## Roles\n"
        "A role describes what model you want and your preferences.\n\n"
        "```yaml\n"
        "roles:\n"
        "  llm.inference:\n"
        "    kind: chat  # one of: chat, embedding, image, audio, tool\n"
        "    description: Main reasoning model for answers.\n"
        "    preferences:\n"
        "      cost: medium    # low | medium | high\n"
        "      latency: medium # low | medium | high\n"
        "      quality: high   # low | medium | high\n"
        "      providers: [openai, anthropic]\n"
        "    # Optional overrides:\n"
        "    # force_provider: openai\n"
        "    # force_model: gpt-4o\n"
        "    # mode_params: {temperature: 0.2}\n"
        "  \n"
        "  llm.embedding:\n"
        "    kind: embedding\n"
        "    description: Vector embeddings for semantic search.\n"
        "    preferences:\n"
        "      cost: low\n"
        "      quality: medium\n"
        "      providers: [openai]\n"
        "```\n\n"
        "Tips:\n"
        "- Use `kind` to match the task (chat vs embedding, etc.).\n"
        "- Set `preferences` to guide model selection.\n"
        "- Use `force_provider`/`force_model` only if you must pin exact choices.\n\n"
        "## Defaults\n"
        "You can set global defaults for provider preference order:\n\n"
        "```yaml\n"
        "defaults:\n"
        "  providers: [openai, anthropic]\n"
        "```\n\n"
        "## What to do next\n"
        "1) Put your API keys in `.env` using the names from `env_key`.\n"
        "2) Edit `llmhub.spec.yaml` to add more roles as your app grows.\n"
        "3) Run `llmhub generate` to build the runtime.\n\n"
        "## For AI Agents\n"
        "If you're an AI agent helping with this project:\n"
        "- **Structured documentation**: See [llmhub.aimanifest.yaml](https://github.com/rethink-paradigms/llm-hub/blob/main/llmhub.aimanifest.yaml) in LLMHub repository\n"
        "- **Capability contracts**: All CLI/Runtime operations documented with input/output schemas\n"
        "- **Schema reference**: Complete SpecConfig and RuntimeConfig schemas available\n\n"
        "## Troubleshooting\n"
        "- **Spec validation errors**: Run `llmhub spec validate`\n"
        "- **Environment issues**: Run `llmhub doctor`\n"
        "- **Generation problems**: Check `llmhub catalog show` to see available models\n"
        "- **Full documentation**: https://github.com/rethink-paradigms/llm-hub\n"
    )
    try:
        guide_path.write_text(guide_content)
        console.print(f"[green]✓ Spec guide created at {guide_path}[/green]")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not write spec guide: {e}[/yellow]")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Review SPEC_GUIDE.md and edit llmhub.spec.yaml")
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
