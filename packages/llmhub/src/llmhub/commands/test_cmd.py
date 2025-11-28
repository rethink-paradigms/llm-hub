import time
import json
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from dotenv import load_dotenv
from llmhub_runtime import LLMHub
from ..context import resolve_context
from ..spec_models import load_spec, SpecError
from ..runtime_io import load_runtime, RuntimeError as RTError
from ..env_manager import check_env
from .. import ux

console = Console()


def test(
    role: Optional[str] = typer.Option(None, "--role", help="Role to test"),
    prompt: Optional[str] = typer.Option(None, "--prompt", help="Prompt to send"),
    env_file: Optional[str] = typer.Option(None, "--env-file", help="Path to .env file"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON response")
) -> None:
    """Test a role with a prompt."""
    context = resolve_context()
    
    if not context.runtime_path.exists():
        console.print(f"[red]No runtime file found at {context.runtime_path}[/red]")
        console.print("Run 'llmhub generate' first")
        raise typer.Exit(1)
    
    try:
        # Load .env if specified
        if env_file:
            load_dotenv(Path(env_file))
        else:
            default_env = context.root / ".env"
            if default_env.exists():
                load_dotenv(default_env)
        
        # Load runtime
        runtime = load_runtime(context.runtime_path)
        
        # Determine role
        test_role = role
        if not test_role:
            # Let user select
            role_names = list(runtime.roles.keys())
            if not role_names:
                console.print("[red]No roles in runtime[/red]")
                raise typer.Exit(1)
            
            test_role = ux.select_from_list("Select role to test:", role_names)
        
        if test_role not in runtime.roles:
            console.print(f"[red]Role '{test_role}' not found in runtime[/red]")
            raise typer.Exit(1)
        
        role_config = runtime.roles[test_role]
        
        # Determine prompt
        test_prompt = prompt
        if not test_prompt:
            test_prompt = ux.prompt_text("Enter test prompt", default="Hello, how are you?")
        
        # Initialize hub
        console.print(f"\n[cyan]Testing role: {test_role}[/cyan]")
        console.print(f"[cyan]Provider: {role_config.provider}[/cyan]")
        console.print(f"[cyan]Model: {role_config.model}[/cyan]")
        console.print(f"[cyan]Mode: {role_config.mode}[/cyan]\n")
        
        try:
            hub = LLMHub(config_path=str(context.runtime_path))
        except Exception as e:
            console.print(f"[red]Failed to initialize LLMHub: {e}[/red]")
            console.print("\n[yellow]Check that required environment variables are set[/yellow]")
            raise typer.Exit(1)
        
        # Make call based on mode
        start = time.time()
        try:
            if role_config.mode == "embedding":
                response = hub.embedding(test_role, test_prompt)
            else:
                # Default to completion for chat and other modes
                messages = [{"role": "user", "content": test_prompt}]
                response = hub.completion(test_role, messages)
            
            duration = time.time() - start
            
            if json_output:
                console.print("\n[bold]Raw Response:[/bold]")
                console.print(json.dumps(response, indent=2))
            else:
                console.print("[green]✓ Call successful[/green]")
                console.print(f"Duration: {duration:.2f}s")
                
                # Try to extract and display content
                if isinstance(response, dict):
                    if "choices" in response and response["choices"]:
                        content = response["choices"][0].get("message", {}).get("content")
                        if content:
                            console.print(f"\n[bold]Response:[/bold]\n{content}\n")
                    elif "data" in response:
                        # Embedding response
                        console.print(f"\n[bold]Embeddings:[/bold] Generated {len(response['data'])} embedding(s)")
                    else:
                        console.print(f"\n[bold]Response:[/bold]\n{response}\n")
                else:
                    console.print(f"\n[bold]Response:[/bold]\n{response}\n")
        
        except Exception as e:
            console.print(f"\n[red]✗ Call failed: {e}[/red]")
            console.print("\n[yellow]Possible issues:[/yellow]")
            console.print("  • Missing or invalid API key")
            console.print("  • Network connectivity")
            console.print("  • Invalid model name")
            raise typer.Exit(1)
        
    except RTError as e:
        console.print(f"[red]Runtime error: {e}[/red]")
        raise typer.Exit(1)


def doctor(
    no_network: bool = typer.Option(False, "--no-network", help="Skip network test calls")
) -> None:
    """Run comprehensive health check."""
    context = resolve_context()
    
    console.print("\n[bold]LLMHub Doctor[/bold]\n")
    
    issues = []
    warnings = []
    
    # Check 1: Spec validation
    console.print("[cyan]1. Checking spec...[/cyan]")
    if not context.spec_path.exists():
        issues.append("No spec file found")
        console.print("   [red]✗ No spec file[/red]")
    else:
        try:
            spec = load_spec(context.spec_path)
            console.print(f"   [green]✓ Spec valid ({len(spec.roles)} roles)[/green]")
        except SpecError as e:
            issues.append(f"Spec validation failed: {e}")
            console.print(f"   [red]✗ {e}[/red]")
            spec = None
    
    # Check 2: Runtime validation
    console.print("[cyan]2. Checking runtime...[/cyan]")
    if not context.runtime_path.exists():
        warnings.append("No runtime file found")
        console.print("   [yellow]⚠ No runtime file[/yellow]")
        runtime = None
    else:
        try:
            runtime = load_runtime(context.runtime_path)
            console.print(f"   [green]✓ Runtime valid ({len(runtime.roles)} roles)[/green]")
        except RTError as e:
            issues.append(f"Runtime validation failed: {e}")
            console.print(f"   [red]✗ {e}[/red]")
            runtime = None
    
    # Check 3: Environment variables
    console.print("[cyan]3. Checking environment...[/cyan]")
    if spec:
        # Try to load .env
        default_env = context.root / ".env"
        if default_env.exists():
            load_dotenv(default_env)
        
        missing = check_env(spec)
        if missing:
            warnings.append(f"{len(missing)} environment variable(s) missing")
            console.print(f"   [yellow]⚠ {len(missing)} variable(s) missing:[/yellow]")
            for mv in missing:
                console.print(f"     • {mv.env_key}")
        else:
            console.print("   [green]✓ All environment variables set[/green]")
    else:
        console.print("   [yellow]⚠ Skipped (no spec)[/yellow]")
    
    # Check 4: Network test call (if not disabled)
    if not no_network and runtime:
        console.print("[cyan]4. Testing network call...[/cyan]")
        
        # Find first chat role
        chat_role = None
        for role_name, role_config in runtime.roles.items():
            if role_config.mode == "chat":
                chat_role = role_name
                break
        
        if chat_role:
            try:
                hub = LLMHub(config_path=str(context.runtime_path))
                messages = [{"role": "user", "content": "Hello"}]
                hub.completion(chat_role, messages)
                console.print(f"   [green]✓ Test call successful ({chat_role})[/green]")
            except Exception as e:
                issues.append(f"Test call failed: {e}")
                console.print(f"   [red]✗ {e}[/red]")
        else:
            console.print("   [yellow]⚠ No chat role to test[/yellow]")
    elif no_network:
        console.print("[cyan]4. Network test skipped[/cyan]")
    else:
        console.print("[cyan]4. Network test skipped (no runtime)[/cyan]")
    
    # Summary
    console.print("\n[bold]Summary:[/bold]\n")
    
    if not issues and not warnings:
        console.print("[green]✓ All checks passed![/green]")
        console.print("\nYour LLMHub setup is ready to use.\n")
    else:
        if issues:
            console.print(f"[red]✗ {len(issues)} issue(s) found:[/red]")
            for issue in issues:
                console.print(f"  • {issue}")
            console.print()
        
        if warnings:
            console.print(f"[yellow]⚠ {len(warnings)} warning(s):[/yellow]")
            for warning in warnings:
                console.print(f"  • {warning}")
            console.print()
        
        if issues:
            raise typer.Exit(1)
