"""Classification + redaction for provider failures. Honest CHP wording:
external constraints are named as external — never disguised as app policy."""

from app.domain.enums import ErrorCategory

REDACTED = "***REDACTED***"

USER_MESSAGES: dict[ErrorCategory, str] = {
    ErrorCategory.AUTH_ERROR: (
        "The provider rejected the credentials. Re-enter the key or provider "
        "settings. Your key was not saved by Context Bridge."
    ),
    ErrorCategory.PROVIDER_LIMIT_ERROR: (
        "The selected provider could not process this request as submitted. "
        "Context Bridge did not apply a hard app limit; this appears to be an "
        "external provider/model constraint. Exact limits depend on the "
        "provider/model and must be verified."
    ),
    ErrorCategory.TIMEOUT: (
        "The provider did not respond in time. This is an external timeout, "
        "not a Context Bridge cap. Retry, try a smaller/faster model, or run "
        "locally."
    ),
    ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE: (
        "The provider could not be reached or returned a server error. Check "
        "the base URL, model name, and service status, then retry."
    ),
    ErrorCategory.HOST_LIMIT_ERROR: (
        "The deployed host could not complete this run. Context Bridge did "
        "not intentionally cap your input/output. For large/private work, "
        "run locally."
    ),
    ErrorCategory.MALFORMED_MODEL_OUTPUT: (
        "The model output missed required structure. Context Bridge "
        "attempted validation/repair and could not fully correct it."
    ),
}

_FALLBACK_MESSAGE = "The provider call failed for an unclassified reason."


def redact(text: str, secrets: list[str]) -> str:
    """Remove every secret value from text. Empty secrets are ignored."""
    for secret in secrets:
        if secret:
            text = text.replace(secret, REDACTED)
    return text


def classify_status(status_code: int) -> ErrorCategory:
    if status_code in (401, 403):
        return ErrorCategory.AUTH_ERROR
    if status_code == 408:
        return ErrorCategory.TIMEOUT
    if status_code in (400, 413, 422, 429):
        return ErrorCategory.PROVIDER_LIMIT_ERROR
    if status_code == 404 or status_code >= 500:
        return ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE
    return ErrorCategory.UNKNOWN_ERROR


def build_provider_error_message(
    category: ErrorCategory, detail: str, secrets: list[str]
) -> str:
    base = USER_MESSAGES.get(category, _FALLBACK_MESSAGE)
    safe_detail = redact(detail, secrets).strip()[:300]
    return f"{base} (Detail: {safe_detail})" if safe_detail else base
