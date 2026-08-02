"""Local Ollama provider via its native generate endpoint. No auth by default.

Connection failures map to concrete local-setup guidance, not a crash.
Endpoint default is the commonly used local port; exact current commands
and defaults are [VERIFY current Ollama docs] in docs/local_ollama.md (M4).
"""

import httpx

from app.application.error_mapper import (
    build_provider_error_message,
    classify_status,
)
from app.domain.enums import ErrorCategory, ProviderMode, StageName
from app.domain.errors import ProviderCallError

DEFAULT_OLLAMA_ENDPOINT = "http://localhost:11434"
DEFAULT_TIMEOUT_SECONDS = 600.0


class OllamaProvider:
    provider_name = "Ollama (local)"
    provider_mode = ProviderMode.LOCAL_OLLAMA
    credential_source = "local_no_auth"

    def __init__(
        self,
        *,
        model_name: str,
        endpoint: str = DEFAULT_OLLAMA_ENDPOINT,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.model_name = model_name
        self._endpoint = endpoint.rstrip("/")
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout_seconds, connect=10.0),
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
                f"{self._endpoint}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": assembled_prompt,
                    "stream": False,
                    "options": {"temperature": 0},
                },
            )
        except httpx.TimeoutException as exc:
            raise ProviderCallError(
                build_provider_error_message(ErrorCategory.TIMEOUT, str(exc), []),
                ErrorCategory.TIMEOUT,
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderCallError(
                "Could not connect to the local Ollama endpoint at "
                f"{self._endpoint}. Local setup checklist: 1) Is Ollama "
                "installed? 2) Is it running (`ollama serve` or the desktop "
                "app)? 3) Is the model pulled (`ollama pull <model>`)? "
                "4) Endpoint/port correct? Exact commands: [VERIFY current "
                "Ollama docs]. Note: a hosted Context Bridge cannot reach "
                "localhost on your machine — run the app locally for local "
                "mode.",
                ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE,
            ) from exc
        if response.status_code != 200:
            category = classify_status(response.status_code)
            detail = f"HTTP {response.status_code}: {response.text[:200]}"
            message = build_provider_error_message(category, detail, [])
            if response.status_code == 404:
                message += (
                    f" If the endpoint is reachable but the model is unknown, "
                    f"pull it first: `ollama pull {self.model_name}` [VERIFY]."
                )
            raise ProviderCallError(message, category)
        try:
            content = response.json()["response"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderCallError(
                build_provider_error_message(
                    ErrorCategory.MALFORMED_MODEL_OUTPUT,
                    "unexpected response shape from Ollama",
                    [],
                ),
                ErrorCategory.MALFORMED_MODEL_OUTPUT,
            ) from exc
        if not isinstance(content, str) or not content.strip():
            raise ProviderCallError(
                build_provider_error_message(
                    ErrorCategory.MALFORMED_MODEL_OUTPUT,
                    "Ollama returned empty content",
                    [],
                ),
                ErrorCategory.MALFORMED_MODEL_OUTPUT,
            )
        return content
