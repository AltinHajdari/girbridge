from pathlib import Path

from girbridge.services.xml_validation_service import XmlValidationService


def _write_simple_schema(path: Path) -> None:
    path.write_text(
        """
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="value" type="xs:string"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_validate_xml_valid_file_schema(tmp_path: Path) -> None:
    xml_file = tmp_path / "target.xml"
    xml_file.write_text("<root><value>ok</value></root>\n", encoding="utf-8")

    schema_file = tmp_path / "schema.xsd"
    _write_simple_schema(schema_file)

    report_file = tmp_path / "report.md"

    service = XmlValidationService()
    result = service.validate_xml(
        xml_path=xml_file,
        schema_path=schema_file,
        report_path=report_file,
    )

    assert result.is_valid is True
    assert result.schema_path == schema_file
    assert result.errors == []
    assert report_file.exists()


def test_validate_xml_invalid_file_schema(tmp_path: Path) -> None:
    xml_file = tmp_path / "target.xml"
    xml_file.write_text("<root><missing>bad</missing></root>\n", encoding="utf-8")

    schema_file = tmp_path / "schema.xsd"
    _write_simple_schema(schema_file)

    service = XmlValidationService()
    result = service.validate_xml(
        xml_path=xml_file,
        schema_path=schema_file,
    )

    assert result.is_valid is False
    assert result.schema_path is None
    assert len(result.errors) >= 1


def test_validate_xml_with_schema_directory(tmp_path: Path) -> None:
    xml_file = tmp_path / "target.xml"
    xml_file.write_text("<root><value>ok</value></root>\n", encoding="utf-8")

    schema_dir = tmp_path / "xsd"
    schema_dir.mkdir()

    invalid_schema = schema_dir / "invalid_schema.xsd"
    invalid_schema.write_text(
        "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>", encoding="utf-8"
    )

    valid_schema = schema_dir / "valid_schema.xsd"
    _write_simple_schema(valid_schema)

    service = XmlValidationService()
    result = service.validate_xml(
        xml_path=xml_file,
        schema_path=schema_dir,
    )

    assert result.is_valid is True
    assert result.schema_path == valid_schema
