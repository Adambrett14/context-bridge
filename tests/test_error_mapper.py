"""Error mapper: redaction, status classification, honest messages."""

from app.application.error_mapper import (
    REDACTED,
    USER_MESSAGES,
    build_provider_error_message,
    classify_status,
    redact,
)
from app.domain.enums import ErrorCategory


def test_redact_removes_secret_values() -> None:
    out = redact("boom sk-abc123 happened with sk-abc123", ["sk-abc123"])
    assert "sk-abc123" not in out
    assert REDACTED in out


def test_redact_ignores_empty_secrets() -> None:
    assert redact("nothing to hide", ["", ""]) == "nothing to hide"


def test_status_classification() -> None:
    assert classify_status(401) is ErrorCategory.AUTH_ERROR
    assert classify_status(403) is ErrorCategory.AUTH_ERROR
    assert classify_status(408) is ErrorCategory.TIMEOUT
    assert classify_status(413) is ErrorCategory.PROVIDER_LIMIT_ERROR
    assert classify_status(429) is ErrorCategory.PROVIDER_LIMIT_ERROR
    assert classify_status(404) is ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE
    assert classify_status(500) is ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE


def test_messages_are_honest_and_redacted() -> None:
    assert "did not apply a hard app limit" in USER_MESSAGES[
        ErrorCategory.PROVIDER_LIMIT_ERROR
    ]
    message = build_provider_error_message(
        ErrorCategory.AUTH_ERROR, "server said: bad key sk-XYZ", ["sk-XYZ"]
    )
    assert "sk-XYZ" not in message
    assert "credentials" in message
