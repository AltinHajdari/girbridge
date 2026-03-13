from pathlib import Path

import typer
from rich.console import Console

from girbridge.core.config import AppConfig
from girbridge.services.mapping_service import MappingService

console = Console()


SOURCE_CONTEXT_OPTION = typer.Option(
    ...,
    "--source-context",
    "-c",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Path to source context file (.txt, .md, or .json).",
)

XSD_PATH_OPTION = typer.Option(
    ...,
    "--xsd-path",
    "-x",
    exists=True,
    readable=True,
    help="Path to an XSD file or a directory containing XSD files.",
)

OUTPUT_PROMPT_OPTION = typer.Option(
    ...,
    "--output-prompt",
    "-o",
    help="Output filepath for the generated prompt text file.",
)

SOURCE_SAMPLE_XML_OPTION = typer.Option(
    None,
    "--source-sample-xml",
    "-s",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Optional path to a representative source XML snippet.",
)

CUSTOMER_NAME_OPTION = typer.Option(
    "unknown_customer",
    "--customer-name",
    help="Customer identifier used in metadata.",
)


def draft_mapping_command(
    source_context: Path = SOURCE_CONTEXT_OPTION,
    xsd_path: Path = XSD_PATH_OPTION,
    output_prompt: Path = OUTPUT_PROMPT_OPTION,
    source_sample_xml: Path | None = SOURCE_SAMPLE_XML_OPTION,
    customer_name: str = CUSTOMER_NAME_OPTION,
) -> None:
    """
    Generate a draft-mapping prompt bundle for manual use in external chatbots.
    """
    config = AppConfig()
    service = MappingService(config=config)

    console.print("[bold blue]Starting draft-mapping prompt generation...[/bold blue]")

    result = service.generate_draft_mapping_prompt(
        source_context_path=source_context,
        xsd_path=xsd_path,
        output_prompt_path=output_prompt,
        customer_name=customer_name,
        source_sample_xml_path=source_sample_xml,
    )

    console.print(f"[green]Prompt written to:[/green] {result.output_prompt_path}")

    attachments_dir = result.output_prompt_path.parent / "attachments"

    console.print("")
    console.print("[bold yellow]Next steps:[/bold yellow]")
    console.print("1. Open your chatbot (ChatGPT, Copilot, etc.)")
    console.print(f"2. Upload all files from: {attachments_dir}")
    console.print(f"3. Paste the prompt from: {result.output_prompt_path}")
    console.print("")
