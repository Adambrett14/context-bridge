"""Context Bridge — Streamlit entrypoint.

M2: the demo runs end-to-end through the real orchestrator with the
DemoProvider (no network, no key). The custom-run form validates source and
demonstrates the SOURCE REQUIRED guard; live providers arrive in M3.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from app.application.pipeline_orchestrator import PipelineOrchestrator  # noqa: E402
from app.application.prompt_assembler import PromptAssembler  # noqa: E402
from app.domain.enums import BridgeMode, ProviderMode  # noqa: E402
from app.domain.errors import ContextBridgeError  # noqa: E402
from app.domain.models import (  # noqa: E402
    SOURCE_REQUIRED_TEXT,
    SourceBundle,
    UserInput,
)
from app.infrastructure.file_loader import load_text_upload  # noqa: E402
from app.infrastructure.providers.demo_provider import DemoProvider  # noqa: E402
from app.ui.stage_tabs import render_stage_results  # noqa: E402

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


def render_custom_tab() -> None:
    st.markdown("**Custom run — bring your own source material.**")
    st.caption(LARGE_RUN_NOTE)
    with st.form("custom_run_form"):
        project_name = st.text_input("Project name (optional)")
        bridge_mode = st.selectbox("Bridge mode", [m.value for m in BridgeMode])
        uploaded = st.file_uploader(
            "Source transcript (.txt / .md)", type=["txt", "md"]
        )
        pasted = st.text_area("Pasted context", height=200)
        objective = st.text_area(
            "Current objective / carry-forward instructions", height=100
        )
        submitted = st.form_submit_button("Check source & prepare run")
    if not submitted:
        return
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
    )
    bundle = SourceBundle.from_user_input(user_input)
    if not bundle.usable_source_present:
        st.error(SOURCE_REQUIRED_TEXT)
        return
    st.success(
        f"Source accepted: {len(bundle.source_parts)} part(s), "
        f"{len(bundle.combined_source_text()):,} characters. "
        "No app-defined cap applied."
    )
    st.info(
        "**Live provider execution arrives in M3** (BYOK / local Ollama). "
        "The Demo tab runs the full pipeline today. Your text was processed "
        "in this session only and is not stored."
    )


def render_local_tab() -> None:
    st.markdown(
        "**Local LLM mode (arrives in M3).** Clone the repo, run Ollama or "
        "another local OpenAI-compatible endpoint, and point Context Bridge "
        "at it. Recommended for private or very large transcripts. Full "
        "setup docs land in M4 (docs/local_ollama.md)."
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
