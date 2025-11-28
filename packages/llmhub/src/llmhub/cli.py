import typer
from .commands import setup_cmd, spec_cmd, runtime_cmd, env_cmd, test_cmd

app = typer.Typer(help="LLMHub CLI — manage LLM specs and runtime configs")

# Top-level commands
app.command(name="setup")(setup_cmd.setup)
app.command(name="init")(setup_cmd.init)
app.command(name="status")(setup_cmd.status)
app.command(name="path")(setup_cmd.path)

# Spec commands
spec_app = typer.Typer(help="Spec management commands")
spec_app.command(name="show")(spec_cmd.spec_show)
spec_app.command(name="validate")(spec_cmd.spec_validate)
app.add_typer(spec_app, name="spec")

# Standalone role commands (for convenience)
app.command(name="roles")(spec_cmd.roles)
app.command(name="add-role")(spec_cmd.add_role)
app.command(name="edit-role")(spec_cmd.edit_role)
app.command(name="rm-role")(spec_cmd.rm_role)

# Runtime commands
app.command(name="generate")(runtime_cmd.generate)
runtime_app = typer.Typer(help="Runtime management commands")
runtime_app.command(name="show")(runtime_cmd.runtime_show)
runtime_app.command(name="diff")(runtime_cmd.diff)
app.add_typer(runtime_app, name="runtime")

# Env commands
env_app = typer.Typer(help="Environment management commands")
env_app.command(name="sync")(env_cmd.env_sync)
env_app.command(name="check")(env_cmd.env_check)
app.add_typer(env_app, name="env")

# Test commands
app.command(name="test")(test_cmd.test)
app.command(name="doctor")(test_cmd.doctor)


# Default behaviour: no command
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """LLMHub CLI - manage LLM specs and runtime configs."""
    if ctx.invoked_subcommand is None:
        # Print summary status
        setup_cmd.print_status_summary()
        
        typer.echo("\nCommon commands:")
        typer.echo("  llmhub init          # quick start with minimal config")
        typer.echo("  llmhub setup         # interactive setup")
        typer.echo("  llmhub generate      # generate runtime from spec")
        typer.echo("  llmhub test          # test a role")
        typer.echo("  llmhub doctor        # run health check")
        typer.echo("\nRun 'llmhub --help' for all commands\n")


if __name__ == "__main__":
    app()
