from pathlib import Path

import typer
from rich.console import Console

from girbridge.services.xml_validation_service import XmlValidationService

console = Console()


TARGET_XML_OPTION = typer.Option(
    ...,
    "--target-xml",
    "-t",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Path to target XML file to validate.",
)

SCHEMA_PATH_OPTION = typer.Option(
    ...,
    "--schema-path",
    "-s",
    exists=True,
    readable=True,
    help="Path to XSD file or directory containing XSD files.",
)

REPORT_FILE_OPTION = typer.Option(
    None,
    "--report-file",
    "-r",
    help="Optional output path for validation report file.",
)


def validate_xml_command(
    target_xml: Path = TARGET_XML_OPTION,
    schema_path: Path = SCHEMA_PATH_OPTION,
    report_file: Path | None = REPORT_FILE_OPTION,
) -> None:
    """
    Validate target XML against XSD schema file(s).
    """
    service = XmlValidationService()

    console.print("[bold blue]Starting validate-xml...[/bold blue]")

    result = service.validate_xml(
        xml_path=target_xml,
        schema_path=schema_path,
        report_path=report_file,
    )

    if result.is_valid:
        console.print("[green]Validation status:[/green] VALID")
        if result.schema_path:
            console.print(f"[green]Schema used:[/green] {result.schema_path}")
        if result.report_path:
            console.print(f"[green]Report written to:[/green] {result.report_path}")
        return

    console.print("[red]Validation status:[/red] INVALID")
    if result.errors:
        console.print("[red]Errors:[/red]")
        for error in result.errors:
            console.print(f"- {error}")
    if result.report_path:
        console.print(f"[yellow]Report written to:[/yellow] {result.report_path}")

    raise typer.Exit(code=1)
