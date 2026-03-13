from girbridge.core.config import AppConfig


def test_app_config_default_prompt_file() -> None:
    config = AppConfig()
    assert config.draft_mapping_prompt_file == "resources/prompts/draft_mapping_system.txt"


def test_app_config_allows_override() -> None:
    config = AppConfig(draft_mapping_prompt_file="resources/prompts/custom.txt")
    assert config.draft_mapping_prompt_file == "resources/prompts/custom.txt"
