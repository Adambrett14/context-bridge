"""Typed exceptions carrying an ErrorCategory. Messages must never contain secrets."""

from app.domain.enums import ErrorCategory


class ContextBridgeError(Exception):
    """Base application error."""

    category: ErrorCategory = ErrorCategory.UNKNOWN_ERROR

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class SourceRequiredError(ContextBridgeError):
    category = ErrorCategory.SOURCE_REQUIRED


class UnsupportedFileTypeError(ContextBridgeError):
    category = ErrorCategory.UNSUPPORTED_FILE_TYPE


class FileDecodeError(ContextBridgeError):
    category = ErrorCategory.FILE_DECODE_ERROR


class MalformedModelOutputError(ContextBridgeError):
    category = ErrorCategory.MALFORMED_MODEL_OUTPUT


class YamlInvalidError(ContextBridgeError):
    category = ErrorCategory.YAML_INVALID


class ProviderCallError(ContextBridgeError):
    """Raised by providers. Message must be user-facing and already redacted."""

    def __init__(self, message: str, category: ErrorCategory) -> None:
        super().__init__(message)
        self.category = category
