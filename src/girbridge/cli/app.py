import typer

from girbridge.cli.draft_mapping import draft_mapping_command

app = typer.Typer(help="GIRBridge CLI - Tools for OECD GIR mapping and transformation.")


@app.callback()
def main() -> None:
    """Root CLI entrypoint."""


app.command("draft-mapping")(draft_mapping_command)
