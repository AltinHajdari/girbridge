from pathlib import Path

import typer
from rich.console import Console

from girbridge.core.config import AppConfig
from girbridge.services.codegen_prompt_service import CodegenPromptService

console = Console()


MAPPING_FILE_OPTION = typer.Option(
    ...,
    "--mapping-file",
    "-m",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Path to the approved or draft mapping YAML file.",
)

OUTPUT_PROMPT_OPTION = typer.Option(
    ...,
    "--output-prompt",
    "-o",
    help="Output path for the generated code prompt text file.",
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

XSD_PATH_OPTION = typer.Option(
    None,
    "--xsd-path",
    "-x",
    exists=True,
    readable=True,
    help="Optional path to an XSD file or a directory containing XSD files.",
)

CUSTOMER_NAME_OPTION = typer.Option(
    "unknown_customer",
    "--customer-name",
    help="Customer identifier used in metadata.",
)

def generate_code_prompt_command(
    mapping_file: Path = MAPPING_FILE_OPTION,
    output_prompt: Path = OUTPUT_PROMPT_OPTION,
    source_sample_xml: Path | None = SOURCE_SAMPLE_XML_OPTION,
    xsd_path: Path | None = XSD_PATH_OPTION,
    customer_name: str = CUSTOMER_NAME_OPTION,
) -> None:
    """
    Generate a code-generation prompt bundle for manual use in external chatbots.
    """
    config = AppConfig(
        draft_mapping_prompt_file="resources/prompts/generate_code_system.txt"
    )
    service = CodegenPromptService(config=config)

    console.print("[bold blue]Starting generate-code-prompt...[/bold blue]")

    result = service.generate_code_prompt(
        mapping_file_path=mapping_file,
        output_prompt_path=output_prompt,
        customer_name=customer_name,
        source_sample_xml_path=source_sample_xml,
        xsd_path=xsd_path,
    )

    console.print(f"[green]Prompt written to:[/green] {result.output_prompt_path}")

    attachments_dir = result.output_prompt_path.parent / "attachments"

    console.print("")
    console.print("[bold yellow]Next steps:[/bold yellow]")
    console.print("1. Open your chatbot (ChatGPT, Copilot, etc.)")
    console.print(f"2. Upload all files from: {attachments_dir}")
    console.print(f"3. Paste the prompt from: {result.output_prompt_path}")
    console.print("")
