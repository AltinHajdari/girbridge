from pathlib import Path

from pydantic import BaseModel, Field


class MappingField(BaseModel):
    id: str
    source_field: str
    target_path: str
    transformation: str = "copy"
    confidence: str = "low"
    rationale: str = ""
    requires_human_review: bool = True
    status: str = "proposed"
    examples: list[str] = Field(default_factory=list)
    reviewer_comment: str = ""


class MappingDocument(BaseModel):
    mapping_version: int = 1
    source_system: str
    target_schema: str = "OECD_GIR"
    fields: list[MappingField] = Field(default_factory=list)


class DraftMappingPromptResult(BaseModel):
    output_prompt_path: Path


class GenerateCodePromptResult(BaseModel):
    output_prompt_path: Path


class MappingDiffResult(BaseModel):
    output_delta_path: Path
    output_report_path: Path
    added_count: int
    removed_count: int
    changed_count: int
