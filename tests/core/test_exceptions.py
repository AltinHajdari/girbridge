from girbridge.core.exceptions import GIRMapperError, PromptFileNotFoundError


def test_prompt_file_not_found_error_inheritance() -> None:
    error = PromptFileNotFoundError("missing")
    assert isinstance(error, PromptFileNotFoundError)
    assert isinstance(error, GIRMapperError)
    assert isinstance(error, Exception)
