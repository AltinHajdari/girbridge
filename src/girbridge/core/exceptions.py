class GIRMapperError(Exception):
    """Base exception for the application."""

    pass


class PromptFileNotFoundError(GIRMapperError):
    """Raised when the prompt template file cannot be found."""

    pass
