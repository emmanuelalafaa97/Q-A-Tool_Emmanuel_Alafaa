# custom exception errors

class LLMAPIError(Exception):
    """Custom exception for LLM API errors."""
    def __init__(self, message: str):
        super().__init__(message)

class FileFormatError(Exception):
    """Custom exception for unsupported file formats."""
    def __init__(self, message: str):
        super().__init__(message)

class ExtractionError(Exception):
    """Custom exception for errors during text extraction."""
    def __init__(self, message: str):
        super().__init__(message)