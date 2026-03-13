from pathlib import Path

import pytest

from girbridge.core.config import AppConfig
from girbridge.core.exceptions import PromptFileNotFoundError
from girbridge.services.mapping_service import MappingService


class _FakeResourcePath:
    def __init__(self, text: str | None = None, missing: bool = False) -> None:
        self._text = text
        self._missing = missing

    def read_text(self, encoding: str = "utf-8") -> str:
        assert encoding == "utf-8"
        if self._missing:
            raise FileNotFoundError("missing")
        assert self._text is not None
        return self._text


class _FakeResourceRoot:
    def __init__(self, resource: _FakeResourcePath) -> None:
        self._resource = resource

    def joinpath(self, path: str) -> _FakeResourcePath:
        assert path
        return self._resource


def test_load_prompt_template_from_packaged_resource(monkeypatch: pytest.MonkeyPatch) -> None:
    service = MappingService(config=AppConfig())
    fake_resource = _FakeResourcePath(text="SYSTEM TEMPLATE")

    monkeypatch.setattr(
        "girbridge.services.mapping_service.resources.files",
        lambda package: _FakeResourceRoot(fake_resource),
    )

    assert service._load_prompt_template() == "SYSTEM TEMPLATE"


def test_load_prompt_template_raises_custom_error_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = MappingService(
        config=AppConfig(draft_mapping_prompt_file="resources/prompts/missing.txt")
    )
    fake_resource = _FakeResourcePath(missing=True)

    monkeypatch.setattr(
        "girbridge.services.mapping_service.resources.files",
        lambda package: _FakeResourceRoot(fake_resource),
    )

    with pytest.raises(PromptFileNotFoundError, match="missing.txt"):
        service._load_prompt_template()


def test_build_prompt_handles_missing_sample_xml() -> None:
    service = MappingService(config=AppConfig())

    prompt = service._build_prompt(
        prompt_template="TEMPLATE",
        customer_name="ACME",
        source_context="CTX",
        attached_files=["a.xsd", "b.xsd"],
    )

    assert "TEMPLATE" in prompt
    assert "## CUSTOMER" in prompt
    assert "ACME" in prompt
    assert "- a.xsd" in prompt
    assert "- b.xsd" in prompt
    assert "## SOURCE SAMPLE XML" not in prompt


def test_copy_attachment_copies_file(tmp_path: Path) -> None:
    service = MappingService(config=AppConfig())
    source = tmp_path / "sample.xml"
    source.write_text("<sample />", encoding="utf-8")
    attachments_dir = tmp_path / "attachments"

    copied_name = service._copy_attachment(source, attachments_dir)

    assert copied_name == "sample.xml"
    assert (attachments_dir / "sample.xml").exists()


def test_copy_xsd_attachments_for_single_file(tmp_path: Path) -> None:
    service = MappingService(config=AppConfig())
    xsd_file = tmp_path / "schema.xsd"
    xsd_file.write_text("<xsd />", encoding="utf-8")
    attachments_dir = tmp_path / "attachments"

    copied = service._copy_xsd_attachments(xsd_file, attachments_dir)

    assert copied == ["schema.xsd"]
    assert (attachments_dir / "schema.xsd").exists()


def test_generate_draft_mapping_prompt_writes_output_and_attachments(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = MappingService(config=AppConfig())
    monkeypatch.setattr(service, "_load_prompt_template", lambda: "PROMPT TEMPLATE")

    source_context = tmp_path / "source.txt"
    source_context.write_text("source context", encoding="utf-8")

    source_sample = tmp_path / "sample.xml"
    source_sample.write_text("<sample/>", encoding="utf-8")

    xsd_dir = tmp_path / "xsds"
    xsd_dir.mkdir()
    xsd_1 = xsd_dir / "a.xsd"
    xsd_2 = xsd_dir / "b.xsd"
    xsd_1.write_text("<xsd a/>", encoding="utf-8")
    xsd_2.write_text("<xsd b/>", encoding="utf-8")

    output_prompt = tmp_path / "out" / "prompt.txt"

    result = service.generate_draft_mapping_prompt(
        source_context_path=source_context,
        xsd_path=xsd_dir,
        output_prompt_path=output_prompt,
        customer_name="Globex",
        source_sample_xml_path=source_sample,
    )

    assert result.output_prompt_path == output_prompt
    assert output_prompt.exists()

    written = output_prompt.read_text(encoding="utf-8")
    assert "PROMPT TEMPLATE" in written
    assert "Globex" in written
    assert "source context" in written
    assert "<sample/>" not in written
    assert "- sample.xml" in written

    attachments_dir = output_prompt.parent / "attachments"
    assert (attachments_dir / "a.xsd").exists()
    assert (attachments_dir / "b.xsd").exists()
    assert (attachments_dir / "sample.xml").exists()
