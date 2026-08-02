"""Stage contract metadata: prompt asset, required tokens, output validation rules."""

from pydantic import BaseModel

from app.domain.enums import StageName

FINAL_NOTICE_SNIPPET = "not automatically stored or transferred"

STAGE_1_HEADINGS: list[str] = [
    "# SOURCE CHECK",
    "# EPISODE MAP",
    "# ATOMIC MEMORY LEDGER",
    "# CONFLICTS AND POSSIBLE SUPERSESSION",
    "# ARTIFACT REGISTER",
    "# MISSING OR UNCERTAIN INFORMATION",
    "# SENSITIVE OR EXCLUDED INFORMATION",
    "# HANDOFF PRIORITIES",
]

CAPSULE_SECTIONS_1_10: list[str] = [
    "1. ASSISTANT ROLE",
    "2. USER'S CURRENT OBJECTIVE",
    "3. CURRENT TASK",
    "4. CONFIRMED REQUIREMENTS",
    "5. CONSTRAINTS",
    "6. DECISIONS MADE",
    "7. WORK COMPLETED",
    "8. CURRENT WORKING STATE",
    "9. ARTIFACT REGISTER",
    "10. REJECTED OR SUPERSEDED DIRECTIONS",
]

CAPSULE_SECTIONS_11_19: list[str] = [
    "11. OPEN QUESTIONS",
    "12. KNOWN RISKS AND UNCERTAINTIES",
    "13. NEXT RECOMMENDED ACTIONS",
    "14. USER PREFERENCES",
    "15. DO NOT FORGET",
    "16. DO NOT ASSUME",
    "17. SOURCE POINTERS",
    "18. SENSITIVE INFORMATION",
    "19. RESUME INSTRUCTION",
]

STAGE_3_HEADINGS: list[str] = [
    "# REQUIRED CORRECTIONS",
    "# UNRESOLVED USER CONFIRMATIONS",
    "# AUDIT VERDICT",
]

COMMON_TOKENS: list[str] = [
    "{{BRIDGE_RULES}}",
    "{{GOVERNANCE_RULES}}",
    "{{PROJECT_NAME}}",
    "{{BRIDGE_MODE}}",
    "{{CURRENT_OBJECTIVE}}",
]


class StageContract(BaseModel):
    stage_name: StageName
    title: str
    prompt_filename: str
    required_tokens: list[str]
    required_headings: list[str]
    requires_markdown_table: bool = False
    is_yaml: bool = False


CONTRACTS: dict[StageName, StageContract] = {
    StageName.STAGE_1_LEDGER: StageContract(
        stage_name=StageName.STAGE_1_LEDGER,
        title="Stage 1 — Atomic Memory Ledger",
        prompt_filename="stage_1_atomic_memory_ledger.md",
        required_tokens=[*COMMON_TOKENS, "{{SOURCE_BUNDLE}}"],
        required_headings=STAGE_1_HEADINGS,
        requires_markdown_table=True,
    ),
    StageName.STAGE_2_DRAFT_CAPSULE: StageContract(
        stage_name=StageName.STAGE_2_DRAFT_CAPSULE,
        title="Stage 2 — Draft Continuity Capsule",
        prompt_filename="stage_2_draft_capsule.md",
        required_tokens=[*COMMON_TOKENS, "{{CAPSULE_SCHEMA}}", "{{LEDGER}}"],
        required_headings=[
            "CAPSULE ID",
            *CAPSULE_SECTIONS_1_10,
            *CAPSULE_SECTIONS_11_19,
        ],
    ),
    StageName.STAGE_3_AUDIT: StageContract(
        stage_name=StageName.STAGE_3_AUDIT,
        title="Stage 3 — Capsule Audit",
        prompt_filename="stage_3_capsule_audit.md",
        required_tokens=[
            *COMMON_TOKENS,
            "{{SOURCE_BUNDLE}}",
            "{{LEDGER}}",
            "{{DRAFT_CAPSULE}}",
        ],
        required_headings=STAGE_3_HEADINGS,
        requires_markdown_table=True,
    ),
    StageName.STAGE_4A_FINAL_A1: StageContract(
        stage_name=StageName.STAGE_4A_FINAL_A1,
        title="Stage 4A — Final Bridge Pack (Sections 1-10)",
        prompt_filename="stage_4a_final_bridge_pack_a1.md",
        required_tokens=[
            *COMMON_TOKENS,
            "{{CAPSULE_SCHEMA}}",
            "{{DRAFT_CAPSULE}}",
            "{{AUDIT}}",
        ],
        required_headings=[
            "# A. HUMAN-READABLE CONTINUITY CAPSULE (Sections 1-10)",
            "CAPSULE ID",
            *CAPSULE_SECTIONS_1_10,
        ],
    ),
    StageName.STAGE_4B_FINAL_A2: StageContract(
        stage_name=StageName.STAGE_4B_FINAL_A2,
        title="Stage 4B — Final Bridge Pack (Sections 11-19)",
        prompt_filename="stage_4b_final_bridge_pack_a2.md",
        required_tokens=[
            *COMMON_TOKENS,
            "{{CAPSULE_SCHEMA}}",
            "{{DRAFT_CAPSULE}}",
            "{{AUDIT}}",
        ],
        required_headings=[
            "# A. HUMAN-READABLE CONTINUITY CAPSULE (Sections 11-19)",
            *CAPSULE_SECTIONS_11_19,
            "# B. MINIMAL NEW-CHAT RESUME PROMPT",
            "# C. ITEMS REQUIRING USER CONFIRMATION",
        ],
    ),
    StageName.STAGE_4C_YAML_STATE: StageContract(
        stage_name=StageName.STAGE_4C_YAML_STATE,
        title="Stage 4C — Machine-Readable YAML State",
        prompt_filename="stage_4c_machine_readable_state.md",
        required_tokens=[*COMMON_TOKENS, "{{DRAFT_CAPSULE}}", "{{AUDIT}}"],
        required_headings=[],
        is_yaml=True,
    ),
}
