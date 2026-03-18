from pathlib import Path

from lxml import etree

from girbridge.adapters.storage import FileStorage
from girbridge.core.models import XmlValidationResult


class XmlValidationService:
    def __init__(self) -> None:
        self.storage = FileStorage()

    def validate_xml(
        self,
        xml_path: Path,
        schema_path: Path,
        report_path: Path | None = None,
    ) -> XmlValidationResult:
        xml_document = etree.parse(str(xml_path))
        schema_candidates = self._resolve_schema_candidates(schema_path)

        if not schema_candidates:
            raise ValueError(f"No .xsd files found in schema path: {schema_path}")

        compiled_errors: list[str] = []
        validation_failures: list[tuple[Path, list[str]]] = []

        for candidate in schema_candidates:
            try:
                parsed_schema = etree.parse(str(candidate))
                xml_schema = etree.XMLSchema(parsed_schema)
            except (etree.XMLSyntaxError, etree.XMLSchemaParseError) as error:
                compiled_errors.append(f"{candidate.name}: {error}")
                continue

            if xml_schema.validate(xml_document):
                result = XmlValidationResult(
                    is_valid=True,
                    xml_path=xml_path,
                    schema_path=candidate,
                    errors=[],
                    report_path=report_path,
                )

                if report_path:
                    self.storage.write_text(report_path, self._build_report(result))

                return result

            errors = [entry.message for entry in xml_schema.error_log]
            validation_failures.append((candidate, errors))

        errors_out: list[str] = []
        if compiled_errors:
            errors_out.extend(compiled_errors)

        if validation_failures:
            for failed_schema, failed_errors in validation_failures:
                errors_out.append(f"Schema `{failed_schema.name}` validation errors:")
                for item in failed_errors:
                    errors_out.append(f"- {item}")

        result = XmlValidationResult(
            is_valid=False,
            xml_path=xml_path,
            schema_path=None,
            errors=errors_out,
            report_path=report_path,
        )

        if report_path:
            self.storage.write_text(report_path, self._build_report(result))

        return result

    def _resolve_schema_candidates(self, schema_path: Path) -> list[Path]:
        if schema_path.is_file():
            return [schema_path]

        return sorted(schema_path.rglob("*.xsd"))

    def _build_report(self, result: XmlValidationResult) -> str:
        lines: list[str] = []
        lines.append("# XML Validation Report")
        lines.append("")
        lines.append(f"- XML file: `{result.xml_path}`")
        lines.append(f"- Status: {'VALID' if result.is_valid else 'INVALID'}")
        if result.schema_path:
            lines.append(f"- Schema used: `{result.schema_path}`")
        lines.append("")

        if result.is_valid:
            lines.append("Validation succeeded.")
            lines.append("")
            return "\n".join(lines)

        lines.append("## Errors")
        lines.append("")
        for error in result.errors:
            lines.append(f"- {error}")
        lines.append("")

        return "\n".join(lines)
