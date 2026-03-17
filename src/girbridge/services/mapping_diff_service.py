from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from girbridge.adapters.storage import FileStorage
from girbridge.core.models import MappingDiffResult

# TODO: The logic is not entirely correct. Reimplement when logic and rules are more clear.

@dataclass(frozen=True)
class _DiffEntry:
    op: str
    path: str
    old_value: Any
    new_value: Any


class MappingDiffService:
    def __init__(self) -> None:
        self.storage = FileStorage()

    def generate_mapping_diff(
        self,
        old_mapping_path: Path,
        new_mapping_path: Path,
        output_delta_path: Path,
        output_report_path: Path,
    ) -> MappingDiffResult:
        old_mapping = self._load_yaml(old_mapping_path)
        new_mapping = self._load_yaml(new_mapping_path)

        changes: list[_DiffEntry] = []
        self._collect_diffs(old_mapping, new_mapping, "$", changes)

        added_count = sum(1 for change in changes if change.op == "add")
        removed_count = sum(1 for change in changes if change.op == "remove")
        changed_count = sum(1 for change in changes if change.op == "replace")

        delta_payload = {
            "delta_version": 1,
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "summary": {
                "added": added_count,
                "removed": removed_count,
                "changed": changed_count,
                "total": len(changes),
            },
            "changes": [
                {
                    "op": change.op,
                    "path": change.path,
                    "old_value": change.old_value,
                    "new_value": change.new_value,
                }
                for change in changes
            ],
        }

        self.storage.write_text(
            output_delta_path,
            yaml.safe_dump(delta_payload, sort_keys=False, allow_unicode=True),
        )

        report = self._build_report(
            old_mapping_path=old_mapping_path,
            new_mapping_path=new_mapping_path,
            changes=changes,
            added_count=added_count,
            removed_count=removed_count,
            changed_count=changed_count,
        )
        self.storage.write_text(output_report_path, report)

        return MappingDiffResult(
            output_delta_path=output_delta_path,
            output_report_path=output_report_path,
            added_count=added_count,
            removed_count=removed_count,
            changed_count=changed_count,
        )

    def _load_yaml(self, path: Path) -> Any:
        content = self.storage.read_text(path)
        loaded = yaml.safe_load(content)
        if loaded is None:
            return {}
        return loaded

    def _collect_diffs(
        self, old_value: Any, new_value: Any, path: str, changes: list[_DiffEntry]
    ) -> None:
        if type(old_value) is not type(new_value):
            changes.append(
                _DiffEntry(
                    op="replace",
                    path=path,
                    old_value=old_value,
                    new_value=new_value,
                )
            )
            return

        if isinstance(old_value, dict):
            old_keys = set(old_value.keys())
            new_keys = set(new_value.keys())

            for key in sorted(old_keys - new_keys, key=str):
                changes.append(
                    _DiffEntry(
                        op="remove",
                        path=self._join_dict_path(path, key),
                        old_value=old_value[key],
                        new_value=None,
                    )
                )

            for key in sorted(new_keys - old_keys, key=str):
                changes.append(
                    _DiffEntry(
                        op="add",
                        path=self._join_dict_path(path, key),
                        old_value=None,
                        new_value=new_value[key],
                    )
                )

            for key in sorted(old_keys & new_keys, key=str):
                self._collect_diffs(
                    old_value[key],
                    new_value[key],
                    self._join_dict_path(path, key),
                    changes,
                )
            return

        if isinstance(old_value, list) :
            if self._collect_diffs_for_id_keyed_list(
                old_list=old_value,
                new_list=new_value,
                path=path,
                changes=changes,
            ):
                return

            common_len = min(len(old_value), len(new_value))

            for index in range(common_len):
                self._collect_diffs(
                    old_value[index],
                    new_value[index],
                    self._join_list_path(path, index),
                    changes,
                )

            for index in range(common_len, len(old_value)):
                changes.append(
                    _DiffEntry(
                        op="remove",
                        path=self._join_list_path(path, index),
                        old_value=old_value[index],
                        new_value=None,
                    )
                )

            for index in range(common_len, len(new_value)):
                changes.append(
                    _DiffEntry(
                        op="add",
                        path=self._join_list_path(path, index),
                        old_value=None,
                        new_value=new_value[index],
                    )
                )
            return

        if old_value != new_value:
            changes.append(
                _DiffEntry(
                    op="replace",
                    path=path,
                    old_value=old_value,
                    new_value=new_value,
                )
            )

    def _build_report(
        self,
        old_mapping_path: Path,
        new_mapping_path: Path,
        changes: list[_DiffEntry],
        added_count: int,
        removed_count: int,
        changed_count: int,
    ) -> str:
        lines: list[str] = []
        lines.append("# Mapping Diff Report")
        lines.append("")
        lines.append(f"- Old mapping: `{old_mapping_path.name}`")
        lines.append(f"- New mapping: `{new_mapping_path.name}`")
        lines.append(f"- Generated (UTC): {datetime.now(UTC).isoformat()}")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append("| Metric | Count |")
        lines.append("|---|---:|")
        lines.append(f"| Added | {added_count} |")
        lines.append(f"| Removed | {removed_count} |")
        lines.append(f"| Changed | {changed_count} |")
        lines.append(f"| Total | {len(changes)} |")
        lines.append("")

        if not changes:
            lines.append("No differences detected.")
            lines.append("")
            return "\n".join(lines)

        lines.append("## Details")
        lines.append("")

        for index, change in enumerate(changes, start=1):
            lines.append(f"### {index}. {change.op.upper()} {change.path}")
            lines.append("")
            lines.append(f"- Old: `{self._format_value(change.old_value)}`")
            lines.append(f"- New: `{self._format_value(change.new_value)}`")
            lines.append("")

        return "\n".join(lines)

    def _join_dict_path(self, base: str, key: Any) -> str:
        return f"{base}.{key}"

    def _join_list_path(self, base: str, index: int) -> str:
        return f"{base}[{index}]"

    def _format_value(self, value: Any) -> str:
        if value is None:
            return "null"
        return json.dumps(value, ensure_ascii=False)

    def _collect_diffs_for_id_keyed_list(
        self,
        old_list: list[Any],
        new_list: list[Any],
        path: str,
        changes: list[_DiffEntry],
    ) -> bool:
        if not old_list and not new_list:
            return True

        if not all(isinstance(item, dict) and "id" in item for item in old_list + new_list):
            return False

        old_ids = [item["id"] for item in old_list]
        new_ids = [item["id"] for item in new_list]

        if len(set(old_ids)) != len(old_ids) or len(set(new_ids)) != len(new_ids):
            return False

        old_by_id = {item["id"]: item for item in old_list}
        new_by_id = {item["id"]: item for item in new_list}

        old_id_set = set(old_by_id.keys())
        new_id_set = set(new_by_id.keys())

        for item_id in sorted(old_id_set - new_id_set, key=str):
            changes.append(
                _DiffEntry(
                    op="remove",
                    path=self._join_dict_path(path, item_id),
                    old_value=old_by_id[item_id],
                    new_value=None,
                )
            )

        for item_id in sorted(new_id_set - old_id_set, key=str):
            changes.append(
                _DiffEntry(
                    op="add",
                    path=self._join_dict_path(path, item_id),
                    old_value=None,
                    new_value=new_by_id[item_id],
                )
            )

        for item_id in sorted(old_id_set & new_id_set, key=str):
            self._collect_diffs(
                old_by_id[item_id],
                new_by_id[item_id],
                self._join_dict_path(path, item_id),
                changes,
            )

        return True
