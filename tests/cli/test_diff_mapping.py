from pathlib import Path

from typer.testing import CliRunner

from girbridge.cli.app import app


class _FakeDiffResult:
    def __init__(
        self,
        output_delta_path: Path,
        output_report_path: Path,
        added_count: int,
        removed_count: int,
        changed_count: int,
    ) -> None:
        self.output_delta_path = output_delta_path
        self.output_report_path = output_report_path
        self.added_count = added_count
        self.removed_count = removed_count
        self.changed_count = changed_count


class _FakeMappingDiffService:
    def generate_mapping_diff(
        self,
        old_mapping_path: Path,
        new_mapping_path: Path,
        output_delta_path: Path,
        output_report_path: Path,
    ) -> _FakeDiffResult:
        assert old_mapping_path.exists()
        assert new_mapping_path.exists()
        return _FakeDiffResult(
            output_delta_path=output_delta_path,
            output_report_path=output_report_path,
            added_count=2,
            removed_count=1,
            changed_count=3,
        )


def test_diff_mapping_cli_command_runs(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    monkeypatch.setattr("girbridge.cli.diff_mapping.MappingDiffService", _FakeMappingDiffService)

    old_mapping = tmp_path / "old_mapping.yaml"
    new_mapping = tmp_path / "new_mapping.yaml"
    old_mapping.write_text("a: 1\n", encoding="utf-8")
    new_mapping.write_text("a: 2\n", encoding="utf-8")

    output_delta = tmp_path / "delta.yaml"
    output_report = tmp_path / "report.md"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "diff-mapping",
            "--old-mapping",
            str(old_mapping),
            "--new-mapping",
            str(new_mapping),
            "--output-delta",
            str(output_delta),
            "--output-report",
            str(output_report),
        ],
    )

    assert result.exit_code == 0
    assert "Delta written to:" in result.stdout
    assert "Report written to:" in result.stdout
