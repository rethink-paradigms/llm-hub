import typer
from .commands import setup, spec, runtime, env, test, catalog

app = typer.Typer(help="LLMHub CLI — manage LLM specs and runtime configs")

# Top-level commands
app.command(name="setup")(setup.setup)
app.command(name="init")(setup.init)
app.command(name="status")(setup.status)
app.command(name="path")(setup.path)

# Spec commands
spec_app = typer.Typer(help="Spec management commands")
spec_app.command(name="show")(spec.spec_show)
spec_app.command(name="validate")(spec.spec_validate)
app.add_typer(spec_app, name="spec")

# Standalone role commands (for convenience)
app.command(name="roles")(spec.roles)
app.command(name="add-role")(spec.add_role)
app.command(name="edit-role")(spec.edit_role)
app.command(name="rm-role")(spec.rm_role)

# Runtime commands
app.command(name="generate")(runtime.generate)
runtime_app = typer.Typer(help="Runtime management commands")
runtime_app.command(name="show")(runtime.runtime_show)
runtime_app.command(name="diff")(runtime.diff)
app.add_typer(runtime_app, name="runtime")

# Env commands
env_app = typer.Typer(help="Environment management commands")
env_app.command(name="sync")(env.env_sync)
env_app.command(name="check")(env.env_check)
app.add_typer(env_app, name="env")

# Test commands
app.command(name="test")(test.test_role)
app.command(name="doctor")(test.doctor)

# Catalog commands
catalog_app = typer.Typer(help="Model catalog management")
catalog_app.command(name="show")(catalog.catalog_show)
catalog_app.command(name="refresh")(catalog.catalog_refresh)
app.add_typer(catalog_app, name="catalog")


# Default behaviour: no command
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """LLMHub CLI - manage LLM specs and runtime configs."""
    if ctx.invoked_subcommand is None:
        # Print summary status
        setup.print_status_summary()
        
        typer.echo("\nCommon commands:")
        typer.echo("  llmhub init          # quick start with minimal config")
        typer.echo("  llmhub setup         # interactive setup")
        typer.echo("  llmhub generate      # generate runtime from spec")
        typer.echo("  llmhub test          # test a role")
        typer.echo("  llmhub doctor        # run health check")
        typer.echo("\nRun 'llmhub --help' for all commands\n")


if __name__ == "__main__":
    app()
