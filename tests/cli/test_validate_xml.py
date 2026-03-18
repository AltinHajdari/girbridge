from pathlib import Path

from typer.testing import CliRunner

from girbridge.cli.app import app


class _FakeValidationResult:
    def __init__(
        self,
        is_valid: bool,
        schema_path: Path | None = None,
        errors: list[str] | None = None,
        report_path: Path | None = None,
    ) -> None:
        self.is_valid = is_valid
        self.schema_path = schema_path
        self.errors = errors or []
        self.report_path = report_path


class _FakeXmlValidationServiceValid:
    def validate_xml(self, xml_path: Path, schema_path: Path, report_path: Path | None = None):  # noqa: ANN001
        assert xml_path.exists()
        assert schema_path.exists()
        return _FakeValidationResult(
            is_valid=True,
            schema_path=schema_path,
            report_path=report_path,
        )


class _FakeXmlValidationServiceInvalid:
    def validate_xml(self, xml_path: Path, schema_path: Path, report_path: Path | None = None):  # noqa: ANN001
        assert xml_path.exists()
        assert schema_path.exists()
        return _FakeValidationResult(
            is_valid=False,
            errors=["Element 'root': Missing child element 'value'."],
            report_path=report_path,
        )


def test_validate_xml_cli_command_valid(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    monkeypatch.setattr(
        "girbridge.cli.validate_xml.XmlValidationService", _FakeXmlValidationServiceValid
    )

    target_xml = tmp_path / "target.xml"
    target_xml.write_text("<root/>\n", encoding="utf-8")

    schema_file = tmp_path / "schema.xsd"
    schema_file.write_text("<xsd/>\n", encoding="utf-8")

    report_file = tmp_path / "report.md"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "validate-xml",
            "--target-xml",
            str(target_xml),
            "--schema-path",
            str(schema_file),
            "--report-file",
            str(report_file),
        ],
    )

    assert result.exit_code == 0
    assert "Validation status:" in result.stdout
    assert "VALID" in result.stdout


def test_validate_xml_cli_command_invalid(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    monkeypatch.setattr(
        "girbridge.cli.validate_xml.XmlValidationService", _FakeXmlValidationServiceInvalid
    )

    target_xml = tmp_path / "target.xml"
    target_xml.write_text("<root/>\n", encoding="utf-8")

    schema_file = tmp_path / "schema.xsd"
    schema_file.write_text("<xsd/>\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "validate-xml",
            "--target-xml",
            str(target_xml),
            "--schema-path",
            str(schema_file),
        ],
    )

    assert result.exit_code == 1
    assert "Validation status:" in result.stdout
    assert "INVALID" in result.stdout
