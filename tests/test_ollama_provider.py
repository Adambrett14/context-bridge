"""Ollama provider: happy path and local-setup guidance on connect failure."""

import httpx
import pytest

from app.domain.enums import ErrorCategory, StageName
from app.domain.errors import ProviderCallError
from app.infrastructure.providers.ollama_provider import OllamaProvider


def make_provider(handler) -> OllamaProvider:
    return OllamaProvider(
        model_name="local-test-model",
        endpoint="http://localhost:11434",
        transport=httpx.MockTransport(handler),
    )


def test_happy_path_returns_response_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/generate"
        return httpx.Response(200, json={"response": "LOCAL OUTPUT"})

    provider = make_provider(handler)
    output = provider.generate_stage_output(
        StageName.STAGE_1_LEDGER, "prompt", {}
    )
    assert output == "LOCAL OUTPUT"


def test_connection_error_gives_local_setup_guidance() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    provider = make_provider(handler)
    with pytest.raises(ProviderCallError) as excinfo:
        provider.generate_stage_output(StageName.STAGE_1_LEDGER, "p", {})
    assert excinfo.value.category is ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE
    message = excinfo.value.message
    assert "Ollama" in message
    assert "localhost:11434" in message
    assert "ollama serve" in message
