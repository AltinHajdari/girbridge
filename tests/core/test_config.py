import pytest
from pydantic import ValidationError

from girbridge.core.config import AppConfig


def test_app_config_requires_prompt_file() -> None:
    with pytest.raises(ValidationError):
        AppConfig()


def test_app_config_allows_override() -> None:
    config = AppConfig(draft_mapping_prompt_file="resources/prompts/custom.txt")
    assert config.draft_mapping_prompt_file == "resources/prompts/custom.txt"
