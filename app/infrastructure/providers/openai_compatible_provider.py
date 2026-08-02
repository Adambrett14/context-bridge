"""OpenAI-compatible chat-completions provider over httpx.

The key lives only on this instance for the active session: never logged,
never in run state, always redacted from error text. `transport` is
injectable so tests run against httpx.MockTransport with zero network.
"""

import httpx

from app.application.error_mapper import (
    build_provider_error_message,
    classify_status,
)
from app.domain.enums import ErrorCategory, ProviderMode, StageName
from app.domain.errors import ProviderCallError

DEFAULT_TIMEOUT_SECONDS = 600.0  # generous by design; no artificial app cap


class OpenAICompatibleProvider:
    def __init__(
        self,
        *,
        base_url: str,
        model_name: str,
        api_key: str,
        provider_name: str = "OpenAI-compatible API",
        provider_mode: ProviderMode = ProviderMode.BYOK_OPENAI_COMPATIBLE,
        credential_source: str = "runtime_user_key",
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.provider_name = provider_name
        self.provider_mode = provider_mode
        self.model_name = model_name
        self.credential_source = credential_source
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout_seconds, connect=15.0),
            transport=transport,
        )

    def generate_stage_output(
        self,
        stage_name: StageName,
        assembled_prompt: str,
        run_metadata: dict[str, str],
    ) -> str:
        try:
            response = self._client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": assembled_prompt}],
                    "temperature": 0,
                },
            )
        except httpx.TimeoutException as exc:
            raise ProviderCallError(
                build_provider_error_message(
                    ErrorCategory.TIMEOUT, str(exc), [self._api_key]
                ),
                ErrorCategory.TIMEOUT,
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderCallError(
                build_provider_error_message(
                    ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE,
                    str(exc),
                    [self._api_key],
                ),
                ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE,
            ) from exc
        if response.status_code != 200:
            category = classify_status(response.status_code)
            detail = f"HTTP {response.status_code}: {_error_detail(response)}"
            raise ProviderCallError(
                build_provider_error_message(category, detail, [self._api_key]),
                category,
            )
        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderCallError(
                build_provider_error_message(
                    ErrorCategory.MALFORMED_MODEL_OUTPUT,
                    "unexpected response shape from provider",
                    [self._api_key],
                ),
                ErrorCategory.MALFORMED_MODEL_OUTPUT,
            ) from exc
        if not isinstance(content, str) or not content.strip():
            raise ProviderCallError(
                build_provider_error_message(
                    ErrorCategory.MALFORMED_MODEL_OUTPUT,
                    "provider returned empty content",
                    [self._api_key],
                ),
                ErrorCategory.MALFORMED_MODEL_OUTPUT,
            )
        return content


def _error_detail(response: httpx.Response) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            message = data.get("error", {}).get("message")
            if isinstance(message, str):
                return message
    except ValueError:
        pass
    return response.text[:200]
