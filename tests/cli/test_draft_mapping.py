from pathlib import Path

from typer.testing import CliRunner

from girbridge.cli.app import app


class _FakeResult:
    def __init__(self, output_prompt_path: Path) -> None:
        self.output_prompt_path = output_prompt_path


class _FakeMappingService:
    def __init__(self, config) -> None:  # noqa: ANN001
        self.config = config

    def generate_draft_mapping_prompt(
        self,
        source_context_path: Path,
        xsd_path: Path,
        output_prompt_path: Path,
        customer_name: str,
        source_sample_xml_path: Path | None = None,
    ) -> _FakeResult:
        assert source_context_path.exists()
        assert xsd_path.exists()
        assert customer_name == "CustomerA"
        assert source_sample_xml_path is None
        return _FakeResult(output_prompt_path=output_prompt_path)


def test_draft_mapping_cli_command_runs(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    monkeypatch.setattr("girbridge.cli.draft_mapping.MappingService", _FakeMappingService)

    source_context = tmp_path / "context.txt"
    source_context.write_text("ctx", encoding="utf-8")

    xsd_file = tmp_path / "schema.xsd"
    xsd_file.write_text("<xsd />", encoding="utf-8")

    output_prompt = tmp_path / "prompt.txt"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "draft-mapping",
            "--source-context",
            str(source_context),
            "--xsd-path",
            str(xsd_file),
            "--output-prompt",
            str(output_prompt),
            "--customer-name",
            "CustomerA",
        ],
    )

    assert result.exit_code == 0
    assert "Prompt written to:" in result.stdout
