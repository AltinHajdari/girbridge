from pathlib import Path

from typer.testing import CliRunner

from girbridge.cli.app import app


class _FakeResult:
    def __init__(self, output_prompt_path: Path) -> None:
        self.output_prompt_path = output_prompt_path


class _FakeCodegenPromptService:
    def __init__(self, config) -> None:  # noqa: ANN001
        self.config = config

    def generate_code_prompt(
        self,
        mapping_file_path: Path,
        output_prompt_path: Path,
        customer_name: str,
        source_sample_xml_path: Path | None = None,
        xsd_path: Path | None = None,
    ) -> _FakeResult:
        assert mapping_file_path.exists()
        assert customer_name == "CustomerA"
        assert source_sample_xml_path is not None
        assert source_sample_xml_path.exists()
        assert xsd_path is not None
        assert xsd_path.exists()
        return _FakeResult(output_prompt_path=output_prompt_path)


def test_generate_code_prompt_cli_command_runs(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    monkeypatch.setattr(
        "girbridge.cli.generate_code_prompt.CodegenPromptService",
        _FakeCodegenPromptService,
    )

    mapping_file = tmp_path / "mapping.yaml"
    mapping_file.write_text("fields: []\n", encoding="utf-8")

    source_sample = tmp_path / "sample.xml"
    source_sample.write_text("<sample />", encoding="utf-8")

    xsd_file = tmp_path / "schema.xsd"
    xsd_file.write_text("<xsd />", encoding="utf-8")

    output_prompt = tmp_path / "prompt.txt"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate-code-prompt",
            "--mapping-file",
            str(mapping_file),
            "--output-prompt",
            str(output_prompt),
            "--source-sample-xml",
            str(source_sample),
            "--xsd-path",
            str(xsd_file),
            "--customer-name",
            "CustomerA",
        ],
    )

    assert result.exit_code == 0
    assert "Prompt written to:" in result.stdout