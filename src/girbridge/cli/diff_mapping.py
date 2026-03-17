from pathlib import Path

import typer
from rich.console import Console

from girbridge.services.mapping_diff_service import MappingDiffService

console = Console()


OLD_MAPPING_OPTION = typer.Option(
    ...,
    "--old-mapping",
    "-a",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Path to the previous mapping YAML file.",
)

NEW_MAPPING_OPTION = typer.Option(
    ...,
    "--new-mapping",
    "-n",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Path to the updated mapping YAML file.",
)

OUTPUT_DELTA_OPTION = typer.Option(
    ...,
    "--output-delta",
    "-d",
    help="Output filepath for the generated mapping delta YAML file.",
)

OUTPUT_REPORT_OPTION = typer.Option(
    ...,
    "--output-report",
    "-r",
    help="Output filepath for the generated markdown diff report.",
)


def diff_mapping_command(
    old_mapping: Path = OLD_MAPPING_OPTION,
    new_mapping: Path = NEW_MAPPING_OPTION,
    output_delta: Path = OUTPUT_DELTA_OPTION,
    output_report: Path = OUTPUT_REPORT_OPTION,
) -> None:
    """
    Generate a YAML delta and markdown report between two mapping files.
    """
    service = MappingDiffService()

    console.print("[bold blue]Starting diff-mapping...[/bold blue]")

    result = service.generate_mapping_diff(
        old_mapping_path=old_mapping,
        new_mapping_path=new_mapping,
        output_delta_path=output_delta,
        output_report_path=output_report,
    )

    console.print(f"[green]Delta written to:[/green] {result.output_delta_path}")
    console.print(f"[green]Report written to:[/green] {result.output_report_path}")
    console.print(
        "[cyan]Summary:[/cyan] "
        f"added={result.added_count}, "
        f"removed={result.removed_count}, "
        f"changed={result.changed_count}"
    )
