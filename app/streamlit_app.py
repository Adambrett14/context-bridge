"""Context Bridge — Streamlit entrypoint.

M3: custom runs execute live against BYOK (OpenAI-compatible), local
Ollama, or an optional owner-secret provider. Demo replay unchanged.
Stateless: nothing is stored server-side; keys never leave the session.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402
from pydantic import SecretStr  # noqa: E402

from app.application.pipeline_orchestrator import PipelineOrchestrator  # noqa: E402
from app.application.prompt_assembler import PromptAssembler  # noqa: E402
from app.domain.enums import BridgeMode, ProviderMode, StageStatus  # noqa: E402
from app.domain.errors import ContextBridgeError  # noqa: E402
from app.domain.models import (  # noqa: E402
    SOURCE_REQUIRED_TEXT,
    PipelineRunState,
    SourceBundle,
    UserInput,
)
from app.infrastructure.file_loader import load_text_upload  # noqa: E402
from app.infrastructure.providers.base import Provider  # noqa: E402
from app.infrastructure.providers.demo_provider import DemoProvider  # noqa: E402
from app.infrastructure.providers.ollama_provider import (  # noqa: E402
    DEFAULT_OLLAMA_ENDPOINT,
    OllamaProvider,
)
from app.infrastructure.providers.openai_compatible_provider import (  # noqa: E402
    OpenAICompatibleProvider,
)
from app.infrastructure.providers.owner_secret_provider import (  # noqa: E402
    build_owner_provider,
)
from app.infrastructure.secrets_reader import read_app_secrets  # noqa: E402
from app.ui.provider_panel import ProviderChoice, render_provider_panel  # noqa: E402
from app.ui.stage_tabs import STAGE_LABELS, render_stage_results  # noqa: E402

APP_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = APP_DIR / "prompts"
SAMPLES_DIR = APP_DIR / "samples"
DEMO_OUTPUTS_DIR = SAMPLES_DIR / "demo_outputs"

LARGE_RUN_NOTE = (
    "Context Bridge sets **no app-defined input/output size caps**. Large "
    "runs may be slow or expensive depending on your provider, and external "
    "model/host/browser limits can still interrupt a run — those are "
    "surfaced honestly as external failures. For private or massive "
    "transcripts, local mode is recommended."
)

EXTERNAL_FAILURE_GUIDANCE = (
    "Options: retry; try a smaller/faster model or another provider; lower "
    "the adaptive chunk threshold in Advanced; or run locally with Ollama. "
    "Context Bridge applied no size cap of its own."
)


def run_demo_pipeline() -> None:
    transcript = (SAMPLES_DIR / "demo_transcript.md").read_text(encoding="utf-8")
    user_input = UserInput(
        project_name="Trailhead Tracker",
        bridge_mode=BridgeMode.STANDARD,
        pasted_context=transcript,
        current_objective="Add CSV export of all logged hikes",
        provider_mode=ProviderMode.DEMO,
    )
    bundle = SourceBundle.from_user_input(user_input)
    orchestrator = PipelineOrchestrator(
        provider=DemoProvider(DEMO_OUTPUTS_DIR),
        assembler=PromptAssembler(PROMPTS_DIR),
    )
    st.session_state["demo_run_state"] = orchestrator.run(bundle)


def render_demo_tab() -> None:
    st.markdown(
        "Runs the **full six-stage pipeline** through the real orchestrator "
        "using the bundled fictional transcript and the DemoProvider "
        "(replayed sample outputs — no API key, no network call)."
    )
    with st.expander("Sample source transcript (fictional)"):
        st.markdown((SAMPLES_DIR / "demo_transcript.md").read_text(encoding="utf-8"))
    st.button("▶️ Run demo pipeline", on_click=run_demo_pipeline, type="primary")
    state = st.session_state.get("demo_run_state")
    if state is not None:
        render_stage_results(state, demo_labeled=True)


def _build_provider(
    choice: ProviderChoice, owner_provider: Provider | None
) -> Provider | None:
    if choice.mode is ProviderMode.OWNER_SECRET:
        if owner_provider is None:
            st.error("Owner provider is not configured on this deployment.")
            return None
        return owner_provider
    if choice.mode is ProviderMode.LOCAL_OLLAMA:
        if not choice.model_name.strip():
            st.error("Enter the local model name to run against Ollama.")
            return None
        return OllamaProvider(
            model_name=choice.model_name.strip(),
            endpoint=choice.endpoint.strip() or DEFAULT_OLLAMA_ENDPOINT,
        )
    missing = [
        name
        for name, value in (
            ("base URL", choice.base_url),
            ("model name", choice.model_name),
            ("API key", choice.api_key),
        )
        if not value.strip()
    ]
    if missing:
        st.error(
            "BYOK needs: " + ", ".join(missing) + ". "
            "(Config completeness — not a size cap.)"
        )
        return None
    return OpenAICompatibleProvider(
        base_url=choice.base_url.strip(),
        model_name=choice.model_name.strip(),
        api_key=choice.api_key,
    )


def _execute_custom_run(
    choice: ProviderChoice,
    owner_provider: Provider | None,
    project_name: str,
    bridge_mode: str,
    uploaded: object,
    pasted: str,
    objective: str,
) -> None:
    uploaded_text: str | None = None
    uploaded_name: str | None = None
    if uploaded is not None:
        try:
            uploaded_text = load_text_upload(uploaded.name, uploaded.getvalue())
            uploaded_name = uploaded.name
        except ContextBridgeError as exc:
            st.error(exc.message)
            return
    user_input = UserInput(
        project_name=project_name or None,
        bridge_mode=BridgeMode(bridge_mode),
        uploaded_source_text=uploaded_text,
        uploaded_source_filename=uploaded_name,
        pasted_context=pasted or None,
        current_objective=objective or None,
        provider_mode=choice.mode,
        model_name=choice.model_name or None,
        base_url=(choice.base_url or choice.endpoint) or None,
        user_api_key=SecretStr(choice.api_key) if choice.api_key else None,
        acknowledge_external_limits=choice.acknowledge_external_limits,
    )
    bundle = SourceBundle.from_user_input(user_input)
    if not bundle.usable_source_present:
        st.error(SOURCE_REQUIRED_TEXT)
        return
    provider = _build_provider(choice, owner_provider)
    if provider is None:
        return
    status = st.status("Running Context Bridge pipeline...", expanded=True)

    def on_start(stage) -> None:
        status.write(f"▶️ {STAGE_LABELS[stage]} — running...")

    def on_complete(result) -> None:
        icon = "✅" if result.status is StageStatus.COMPLETE else "❌"
        status.write(f"{icon} {STAGE_LABELS[result.stage_name]}")

    orchestrator = PipelineOrchestrator(
        provider,
        PromptAssembler(PROMPTS_DIR),
        chunk_threshold_chars=choice.chunk_threshold_chars,
        on_stage_start=on_start,
        on_stage_complete=on_complete,
    )
    state = orchestrator.run(bundle)
    st.session_state["custom_run_state"] = state
    status.update(
        label=f"Pipeline finished: {state.final_status}",
        state="complete" if state.final_status == "complete" else "error",
        expanded=False,
    )


def _render_run_outcome(state: PipelineRunState) -> None:
    for warning in state.user_visible_warnings:
        st.warning(warning)
    if state.final_status != "complete":
        shown = set()
        for result in state.all_results():
            for error in result.errors:
                if error not in shown:
                    st.error(error)
                    shown.add(error)
        if state.final_status == "failed_external_limit":
            st.info(EXTERNAL_FAILURE_GUIDANCE)
    render_stage_results(state, demo_labeled=False)


def render_custom_tab() -> None:
    st.markdown("**Custom run — your source, your provider.**")
    st.caption(LARGE_RUN_NOTE)
    owner_provider = build_owner_provider(read_app_secrets())
    choice = render_provider_panel(owner_available=owner_provider is not None)
    st.divider()
    project_name = st.text_input("Project name (optional)")
    bridge_mode = st.selectbox("Bridge mode", [m.value for m in BridgeMode])
    uploaded = st.file_uploader("Source transcript (.txt / .md)", type=["txt", "md"])
    pasted = st.text_area("Pasted context", height=200)
    objective = st.text_area(
        "Current objective / carry-forward instructions", height=100
    )
    if st.button("🚀 Run Context Bridge", type="primary"):
        _execute_custom_run(
            choice, owner_provider, project_name, bridge_mode,
            uploaded, pasted, objective,
        )
    state = st.session_state.get("custom_run_state")
    if state is not None:
        _render_run_outcome(state)


def render_local_tab() -> None:
    st.markdown(
        "**Run Context Bridge locally with a local model** — recommended "
        "for private or very large transcripts.\n\n"
        "1. Clone the repo and follow the README local setup (venv, "
        "`pip install -r requirements.txt`, `streamlit run "
        "app/streamlit_app.py`).\n"
        "2. Install and start Ollama, then pull a model. Exact commands: "
        "[VERIFY current Ollama docs].\n"
        f"3. In **Custom run → Local Ollama**, set the endpoint (default "
        f"`{DEFAULT_OLLAMA_ENDPOINT}` [VERIFY]) and your pulled model name.\n"
        "4. Run — your transcript never leaves your machine.\n\n"
        "**Note:** this hosted page cannot reach `localhost` on your "
        "computer. Local mode means running the app locally too. Full "
        "walkthrough lands in `docs/local_ollama.md` (M4)."
    )


def render_privacy_notice() -> None:
    with st.expander("Privacy & safety notice", expanded=False):
        st.markdown(
            "- Context Bridge does **not** intentionally store transcripts "
            "or API keys. No accounts, no database, no server-side history.\n"
            "- BYOK keys are masked, used only at runtime, and never written "
            "to logs, exports, or disk.\n"
            "- For private or very large transcripts, run the app locally "
            "with a local model.\n"
            "- External providers you connect to have their own retention "
            "terms [VERIFY per provider].\n"
            "- Review generated bridge packs and remove anything sensitive "
            "before saving or sharing them."
        )


def main() -> None:
    st.set_page_config(page_title="Context Bridge", page_icon="🌉", layout="wide")
    st.title("🌉 Context Bridge")
    st.markdown(
        "**Evidence-based AI handoff generator.** Converts long AI "
        "conversations and project notes into a verified, portable "
        "continuity package: **Source → Ledger → Capsule → Audit → "
        "Final Pack → YAML.**"
    )
    if st.button("🧹 Clear session"):
        st.session_state.clear()
        st.rerun()

    demo_tab, custom_tab, local_tab = st.tabs(
        ["🎬 Demo", "🛠️ Custom run", "💻 Run locally"]
    )
    with demo_tab:
        render_demo_tab()
    with custom_tab:
        render_custom_tab()
    with local_tab:
        render_local_tab()
    render_privacy_notice()


main()
