from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    draft_mapping_prompt_file: str = Field(default="resources/prompts/draft_mapping_system.txt")
