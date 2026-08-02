"""OpenAI-compatible provider against httpx.MockTransport. Zero network."""

import httpx
import pytest

from app.domain.enums import ErrorCategory, StageName
from app.domain.errors import ProviderCallError
from app.infrastructure.providers.openai_compatible_provider import (
    OpenAICompatibleProvider,
)

KEY = "sk-FAKE-test-key-999"


def make_provider(handler) -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        base_url="https://api.example.test/v1",
        model_name="test-model",
        api_key=KEY,
        transport=httpx.MockTransport(handler),
    )


def test_happy_path_returns_content() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        assert request.headers["Authorization"] == f"Bearer {KEY}"
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "STAGE OUTPUT"}}]}
        )

    provider = make_provider(handler)
    output = provider.generate_stage_output(
        StageName.STAGE_1_LEDGER, "prompt", {}
    )
    assert output == "STAGE OUTPUT"


def test_auth_error_is_classified_and_redacted() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401, json={"error": {"message": f"invalid key {KEY}"}}
        )

    provider = make_provider(handler)
    with pytest.raises(ProviderCallError) as excinfo:
        provider.generate_stage_output(StageName.STAGE_1_LEDGER, "p", {})
    assert excinfo.value.category is ErrorCategory.AUTH_ERROR
    assert KEY not in str(excinfo.value)
    assert "credentials" in excinfo.value.message


def test_rate_limit_is_external_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"message": "rate limited"}})

    provider = make_provider(handler)
    with pytest.raises(ProviderCallError) as excinfo:
        provider.generate_stage_output(StageName.STAGE_1_LEDGER, "p", {})
    assert excinfo.value.category is ErrorCategory.PROVIDER_LIMIT_ERROR
    assert "did not apply a hard app limit" in excinfo.value.message


def test_connect_error_is_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    provider = make_provider(handler)
    with pytest.raises(ProviderCallError) as excinfo:
        provider.generate_stage_output(StageName.STAGE_1_LEDGER, "p", {})
    assert excinfo.value.category is ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE
    assert KEY not in str(excinfo.value)
