import typer

from girbridge.cli.diff_mapping import diff_mapping_command
from girbridge.cli.draft_mapping import draft_mapping_command
from girbridge.cli.generate_code_prompt import generate_code_prompt_command

app = typer.Typer(help="GIRBridge CLI - Tools for OECD GIR mapping and transformation.")


@app.callback()
def main() -> None:
    """Root CLI entrypoint."""


app.command("draft-mapping")(draft_mapping_command)
app.command("generate-code-prompt")(generate_code_prompt_command)
app.command("diff-mapping")(diff_mapping_command)
