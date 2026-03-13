from pathlib import Path

from girbridge.core.models import DraftMappingPromptResult, MappingDocument, MappingField


def test_mapping_field_defaults() -> None:
    field = MappingField(id="f1", source_field="source", target_path="/target")
    assert field.transformation == "copy"
    assert field.confidence == "low"
    assert field.requires_human_review is True
    assert field.examples == []


def test_mapping_document_defaults() -> None:
    document = MappingDocument(source_system="legacy")
    assert document.mapping_version == 1
    assert document.target_schema == "OECD_GIR"
    assert document.fields == []


def test_draft_mapping_prompt_result_holds_path() -> None:
    result = DraftMappingPromptResult(output_prompt_path=Path("output/prompt.txt"))
    assert result.output_prompt_path == Path("output/prompt.txt")
