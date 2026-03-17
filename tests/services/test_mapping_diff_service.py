# from pathlib import Path

# import yaml

# from girbridge.services.mapping_diff_service import MappingDiffService


# def test_generate_mapping_diff_writes_delta_and_report(tmp_path: Path) -> None:
#     old_mapping = tmp_path / "old_mapping.yaml"
#     new_mapping = tmp_path / "new_mapping.yaml"

#     old_mapping.write_text(
#         """
# mapping_version: 1
# source_system: SYS_A
# fields:
#   - id: f1
#     target_path: $.a
#     transformation: copy
#   - id: f2
#     target_path: $.b
#     transformation: copy
# """.strip()
#         + "\n",
#         encoding="utf-8",
#     )

#     new_mapping.write_text(
#         """
# mapping_version: 2
# source_system: SYS_A
# fields:
#   - id: f1
#     target_path: $.a.changed
#     transformation: copy
#   - id: f3
#     target_path: $.c
#     transformation: concat
# new_flag: true
# """.strip()
#         + "\n",
#         encoding="utf-8",
#     )

#     output_delta = tmp_path / "delta.yaml"
#     output_report = tmp_path / "report.md"

#     service = MappingDiffService()
#     result = service.generate_mapping_diff(
#         old_mapping_path=old_mapping,
#         new_mapping_path=new_mapping,
#         output_delta_path=output_delta,
#         output_report_path=output_report,
#     )

#     assert output_delta.exists()
#     assert output_report.exists()
#     assert result.added_count >= 1
#     assert result.changed_count >= 1

#     delta_content = yaml.safe_load(output_delta.read_text(encoding="utf-8"))
#     assert delta_content["summary"]["total"] == len(delta_content["changes"])

#     ops = {entry["op"] for entry in delta_content["changes"]}
#     assert "add" in ops
#     assert "replace" in ops

#     report_content = output_report.read_text(encoding="utf-8")
#     assert "# Mapping Diff Report" in report_content
#     assert "## Summary" in report_content
#     assert "## Details" in report_content


# def test_generate_mapping_diff_no_changes(tmp_path: Path) -> None:
#     old_mapping = tmp_path / "old_mapping.yaml"
#     new_mapping = tmp_path / "new_mapping.yaml"

#     content = (
#         """
# mapping_version: 1
# fields:
#   - id: f1
#     target_path: $.a
# """.strip()
#         + "\n"
#     )

#     old_mapping.write_text(content, encoding="utf-8")
#     new_mapping.write_text(content, encoding="utf-8")

#     output_delta = tmp_path / "delta.yaml"
#     output_report = tmp_path / "report.md"

#     service = MappingDiffService()
#     result = service.generate_mapping_diff(
#         old_mapping_path=old_mapping,
#         new_mapping_path=new_mapping,
#         output_delta_path=output_delta,
#         output_report_path=output_report,
#     )

#     assert result.added_count == 0
#     assert result.removed_count == 0
#     assert result.changed_count == 0

#     delta_content = yaml.safe_load(output_delta.read_text(encoding="utf-8"))
#     assert delta_content["summary"]["total"] == 0
#     assert delta_content["changes"] == []

#     report_content = output_report.read_text(encoding="utf-8")
#     assert "No differences detected." in report_content


# def test_generate_mapping_diff_reordered_id_list_no_changes(tmp_path: Path) -> None:
#     old_mapping = tmp_path / "old_mapping.yaml"
#     new_mapping = tmp_path / "new_mapping.yaml"

#     old_mapping.write_text(
#         """
# fields:
#   - id: f1
#     target_path: $.a
#   - id: f2
#     target_path: $.b
# """.strip()
#         + "\n",
#         encoding="utf-8",
#     )

#     new_mapping.write_text(
#         """
# fields:
#   - id: f2
#     target_path: $.b
#   - id: f1
#     target_path: $.a
# """.strip()
#         + "\n",
#         encoding="utf-8",
#     )

#     output_delta = tmp_path / "delta.yaml"
#     output_report = tmp_path / "report.md"

#     service = MappingDiffService()
#     result = service.generate_mapping_diff(
#         old_mapping_path=old_mapping,
#         new_mapping_path=new_mapping,
#         output_delta_path=output_delta,
#         output_report_path=output_report,
#     )

#     assert result.added_count == 0
#     assert result.removed_count == 0
#     assert result.changed_count == 0

#     delta_content = yaml.safe_load(output_delta.read_text(encoding="utf-8"))
#     assert delta_content["summary"]["total"] == 0
