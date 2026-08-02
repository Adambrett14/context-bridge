"""Provider settings panel for custom runs. Keys are masked and session-only."""

from dataclasses import dataclass

import streamlit as st

from app.application.chunk_coordinator import DEFAULT_CHUNK_THRESHOLD_CHARS
from app.domain.enums import ProviderMode
from app.infrastructure.providers.ollama_provider import DEFAULT_OLLAMA_ENDPOINT

BYOK_LABEL = "Bring Your Own Key (OpenAI-compatible)"
OLLAMA_LABEL = "Local Ollama"
OWNER_LABEL = "Owner-configured provider"


@dataclass
class ProviderChoice:
    mode: ProviderMode
    base_url: str = ""
    model_name: str = ""
    api_key: str = ""
    endpoint: str = ""
    chunk_threshold_chars: int = DEFAULT_CHUNK_THRESHOLD_CHARS
    acknowledge_external_limits: bool = False


def _clear_byok_key() -> None:
    st.session_state.pop("byok_api_key", None)


def render_provider_panel(*, owner_available: bool) -> ProviderChoice:
    options = [BYOK_LABEL, OLLAMA_LABEL]
    if owner_available:
        options.append(OWNER_LABEL)
    label = st.radio("Provider for this run", options)
    if label == BYOK_LABEL:
        mode = ProviderMode.BYOK_OPENAI_COMPATIBLE
    elif label == OLLAMA_LABEL:
        mode = ProviderMode.LOCAL_OLLAMA
    else:
        mode = ProviderMode.OWNER_SECRET
    choice = ProviderChoice(mode=mode)

    if mode is ProviderMode.BYOK_OPENAI_COMPATIBLE:
        choice.base_url = st.text_input(
            "Base URL",
            value="https://api.openai.com/v1",
            help=(
                "Any OpenAI-compatible endpoint. Exact provider "
                "compatibility and current model names: [VERIFY provider "
                "docs]."
            ),
        )
        choice.model_name = st.text_input(
            "Model name",
            placeholder="check your provider's current model list [VERIFY]",
        )
        choice.api_key = st.text_input(
            "API key",
            type="password",
            key="byok_api_key",
            help=(
                "Masked; used only for this session's requests; never "
                "stored, logged, exported, or written to disk."
            ),
        )
        st.button("🔐 Clear key", on_click=_clear_byok_key)
    elif mode is ProviderMode.LOCAL_OLLAMA:
        choice.endpoint = st.text_input(
            "Local endpoint", value=DEFAULT_OLLAMA_ENDPOINT
        )
        choice.model_name = st.text_input(
            "Local model name",
            placeholder="a model you have pulled locally [VERIFY ollama list]",
        )
        st.caption(
            "Local mode needs the app AND Ollama running on the same "
            "machine (or an endpoint you can genuinely reach). A hosted "
            "Context Bridge cannot see your laptop's localhost."
        )
    else:
        st.caption(
            "Uses the deployment's own secret configuration. The key is "
            "never shown, logged, or exported."
        )

    with st.expander("Advanced (soft settings — never refusal caps)"):
        choice.chunk_threshold_chars = int(
            st.number_input(
                "Adaptive chunk threshold (characters)",
                min_value=1_000,
                value=DEFAULT_CHUNK_THRESHOLD_CHARS,
                step=5_000,
                help=(
                    "Soft split size for Stage 1 chunk-and-merge on large "
                    "sources. Not a cap: larger inputs are chunked, never "
                    "refused."
                ),
            )
        )
    choice.acknowledge_external_limits = st.checkbox(
        "I understand external provider/model/host limits may still "
        "interrupt very large runs (non-blocking).",
        value=False,
    )
    return choice
