"""Stage output panels with per-stage and combined downloads for a pipeline run.

Expanders (not nested tabs) per CHP large-output strategy: lightweight
display, full content always downloadable, nothing silently trimmed.
"""

import streamlit as st

from app.application.export_builder import EXPORT_FILENAMES, build_final_outputs
from app.domain.enums import STAGE_ORDER, StageName, StageStatus
from app.domain.models import PipelineRunState

STAGE_LABELS: dict[StageName, str] = {
    StageName.STAGE_1_LEDGER: "Stage 1 — Atomic Memory Ledger",
    StageName.STAGE_2_DRAFT_CAPSULE: "Stage 2 — Draft Continuity Capsule",
    StageName.STAGE_3_AUDIT: "Stage 3 — Capsule Audit",
    StageName.STAGE_4A_FINAL_A1: "Stage 4A — Final Bridge Pack (Sections 1-10)",
    StageName.STAGE_4B_FINAL_A2: "Stage 4B — Final Bridge Pack (Sections 11-19)",
    StageName.STAGE_4C_YAML_STATE: "Stage 4C — Machine-Readable YAML State",
}

STATUS_ICONS: dict[StageStatus, str] = {
    StageStatus.NOT_STARTED: "⬜",
    StageStatus.RUNNING: "🔄",
    StageStatus.COMPLETE: "✅",
    StageStatus.FAILED: "❌",
}

DOWNLOAD_FILENAMES: dict[StageName, str] = {
    StageName.STAGE_1_LEDGER: EXPORT_FILENAMES["ledger"],
    StageName.STAGE_2_DRAFT_CAPSULE: "context_bridge_draft_capsule.md",
    StageName.STAGE_3_AUDIT: EXPORT_FILENAMES["audit"],
    StageName.STAGE_4A_FINAL_A1: "context_bridge_final_pack_a1.md",
    StageName.STAGE_4B_FINAL_A2: "context_bridge_final_pack_a2.md",
    StageName.STAGE_4C_YAML_STATE: EXPORT_FILENAMES["yaml_state"],
}


def render_stage_results(state: PipelineRunState, *, demo_labeled: bool) -> None:
    if demo_labeled:
        st.info(
            "These outputs are the bundled **demo replay** — clearly labeled "
            "sample results, so the public demo always works with no API key."
        )
    for stage in STAGE_ORDER:
        result = state.get_result(stage)
        if result is None:
            continue
        icon = STATUS_ICONS[result.status]
        with st.expander(f"{icon} {STAGE_LABELS[stage]}", expanded=False):
            if result.errors:
                st.error(" / ".join(result.errors))
            if result.output_text:
                if stage is StageName.STAGE_4C_YAML_STATE:
                    st.code(result.output_text, language="yaml")
                else:
                    st.markdown(result.output_text)
                st.download_button(
                    label="⬇️ Download this stage output",
                    data=result.output_text,
                    file_name=DOWNLOAD_FILENAMES[stage],
                    mime="text/plain",
                    key=f"download_{state.run_id}_{stage.value}",
                )
    if state.final_status == "complete":
        _render_combined_downloads(state)


def _render_combined_downloads(state: PipelineRunState) -> None:
    outputs = build_final_outputs(state)
    st.subheader("Combined downloads")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "⬇️ Full bridge pack (.md)",
            data=outputs.combined_bridge_pack_md,
            file_name=EXPORT_FILENAMES["full_pack"],
            mime="text/markdown",
            key=f"download_{state.run_id}_full_pack",
        )
    with col2:
        st.download_button(
            "⬇️ YAML state (.yaml)",
            data=outputs.yaml_state,
            file_name=EXPORT_FILENAMES["yaml_state"],
            mime="text/yaml",
            key=f"download_{state.run_id}_yaml",
        )
    with col3:
        st.download_button(
            "⬇️ Resume prompt (.txt)",
            data=outputs.resume_prompt,
            file_name=EXPORT_FILENAMES["resume_prompt"],
            mime="text/plain",
            key=f"download_{state.run_id}_resume",
        )
    st.text_area(
        "Copy-ready resume prompt",
        value=outputs.resume_prompt,
        height=200,
        key=f"resume_text_{state.run_id}",
    )
