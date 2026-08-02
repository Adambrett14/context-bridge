"""Context Bridge — Streamlit entrypoint (M1 skeleton shell).

Thin entrypoint by design: full UI/pipeline modules land in M2-M3.
Displays the bundled demo fixtures so the skeleton is verifiable end to end.
"""

from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
SAMPLES_DIR = APP_DIR / "samples"
DEMO_OUTPUTS_DIR = SAMPLES_DIR / "demo_outputs"

DEMO_STAGES: list[tuple[str, str]] = [
    ("Stage 1 — Atomic Memory Ledger", "stage_1_ledger.md"),
    ("Stage 2 — Draft Continuity Capsule", "stage_2_draft_capsule.md"),
    ("Stage 3 — Capsule Audit", "stage_3_audit.md"),
    ("Stage 4A — Final Bridge Pack (Sections 1-10)", "stage_4a_final_a1.md"),
    ("Stage 4B — Final Bridge Pack (Sections 11-19)", "stage_4b_final_a2.md"),
    ("Stage 4C — Machine-Readable YAML State", "stage_4c_state.yaml"),
]

MODE_NOTES: dict[str, str] = {
    "Demo (no key needed)": "Replays bundled, clearly-labeled sample outputs. Active now.",
    "Bring Your Own Key": "Runs the live pipeline against your provider. Arrives in M3.",
    "Local LLM (Ollama)": "Points the app at your local endpoint. Arrives in M3.",
}


def read_text(path: Path) -> str:
    """Load a bundled text asset."""
    return path.read_text(encoding="utf-8")


def render_demo_tab() -> None:
    st.info(
        "**Demo replay.** These are bundled sample outputs generated from the "
        "fictional transcript below, so the demo always works with no API key. "
        "Live generation on your own text arrives with BYOK/local modes."
    )
    with st.expander("Sample source transcript (fictional)"):
        st.markdown(read_text(SAMPLES_DIR / "demo_transcript.md"))
    for label, filename in DEMO_STAGES:
        with st.expander(label):
            content = read_text(DEMO_OUTPUTS_DIR / filename)
            if filename.endswith(".yaml"):
                st.code(content, language="yaml")
            else:
                st.markdown(content)


def render_custom_tab() -> None:
    st.markdown(
        "**Custom runs arrive in M2-M3.** This tab will hold the input form: "
        "project name, bridge mode (Standard / Detailed / Emergency), .txt/.md "
        "upload, pasted context, current objective, and provider settings "
        "(BYOK key is masked, runtime-only, never stored)."
    )
    st.caption(
        "Context Bridge sets no app-defined input/output size caps. External "
        "provider/model/host limits are surfaced honestly when they occur."
    )


def render_local_tab() -> None:
    st.markdown(
        "**Local LLM mode (arrives in M3).** Clone the repo, run Ollama or "
        "another local OpenAI-compatible endpoint, and point Context Bridge at "
        "it. Recommended for private or very large transcripts. Full setup "
        "docs land in M4 (docs/local_ollama.md)."
    )


def render_privacy_notice() -> None:
    with st.expander("Privacy & safety notice", expanded=False):
        st.markdown(
            "- Context Bridge does **not** intentionally store transcripts or "
            "API keys. No accounts, no database, no server-side history.\n"
            "- BYOK keys are masked, used only at runtime, and never written "
            "to logs, exports, or disk.\n"
            "- For private or very large transcripts, run the app locally "
            "with a local model.\n"
            "- External providers you connect to have their own retention "
            "terms [VERIFY per provider]."
        )


def main() -> None:
    st.set_page_config(page_title="Context Bridge", page_icon="🌉", layout="wide")
    st.title("🌉 Context Bridge")
    st.markdown(
        "**Evidence-based AI handoff generator.** Converts long AI "
        "conversations and project notes into a verified, portable continuity "
        "package: Source → Ledger → Capsule → Audit → Final Pack → YAML."
    )
    mode = st.radio("Provider mode", list(MODE_NOTES), horizontal=True)
    st.caption(MODE_NOTES[mode])

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
