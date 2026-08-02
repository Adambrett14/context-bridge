"""Build user-facing export artifacts. Exports must never contain secrets."""

from app.domain.enums import StageName
from app.domain.models import FinalOutputs, PipelineRunState

EXPORT_FILENAMES: dict[str, str] = {
    "full_pack": "context_bridge_full_pack.md",
    "yaml_state": "context_bridge_state.yaml",
    "ledger": "context_bridge_atomic_memory_ledger.md",
    "audit": "context_bridge_capsule_audit.md",
    "resume_prompt": "context_bridge_resume_prompt.txt",
}

RESUME_HEADING = "# B. MINIMAL NEW-CHAT RESUME PROMPT"
CONFIRMATIONS_HEADING = "# C. ITEMS REQUIRING USER CONFIRMATION"
FINAL_NOTICE_PREFIX = "This bridge package"


def _section_between(text: str, start: str, end: str | None) -> str:
    if start not in text:
        return ""
    tail = text.split(start, 1)[1]
    if end is not None and end in tail:
        tail = tail.split(end, 1)[0]
    return tail.strip()


def extract_resume_prompt(final_a2_md: str) -> str:
    return _section_between(final_a2_md, RESUME_HEADING, CONFIRMATIONS_HEADING)


def extract_unresolved_confirmations(final_a2_md: str) -> str:
    return _section_between(final_a2_md, CONFIRMATIONS_HEADING, FINAL_NOTICE_PREFIX)


def _output_of(state: PipelineRunState, stage: StageName) -> str:
    result = state.get_result(stage)
    return result.output_text if result is not None else ""


def build_combined_pack(state: PipelineRunState, a1: str, a2: str) -> str:
    meta = state.selected_provider_metadata
    lines = [
        "# CONTEXT BRIDGE — FULL BRIDGE PACK",
        "",
        f"- Run ID: {state.run_id}",
        f"- Provider mode: {state.mode.value}",
        f"- Provider: {meta.get('provider_name', 'Not supplied')}",
        f"- Generated at: {state.updated_at.isoformat()}",
        "",
        a1,
        "",
        a2,
        "",
        "---",
        "Machine-readable state: download context_bridge_state.yaml separately.",
        "",
    ]
    return "\n".join(lines)


def build_final_outputs(state: PipelineRunState) -> FinalOutputs:
    a1 = _output_of(state, StageName.STAGE_4A_FINAL_A1)
    a2 = _output_of(state, StageName.STAGE_4B_FINAL_A2)
    return FinalOutputs(
        atomic_memory_ledger_md=_output_of(state, StageName.STAGE_1_LEDGER),
        draft_capsule_md=_output_of(state, StageName.STAGE_2_DRAFT_CAPSULE),
        audit_md=_output_of(state, StageName.STAGE_3_AUDIT),
        final_pack_a1_md=a1,
        final_pack_a2_md=a2,
        yaml_state=_output_of(state, StageName.STAGE_4C_YAML_STATE),
        combined_bridge_pack_md=build_combined_pack(state, a1, a2),
        resume_prompt=extract_resume_prompt(a2),
        unresolved_confirmations=extract_unresolved_confirmations(a2),
    )
