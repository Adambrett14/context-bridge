"""Core domain models. Run state and exports must never contain raw API keys."""

from datetime import UTC, datetime
from typing import ClassVar

from pydantic import BaseModel, Field, SecretStr

from app.domain.enums import (
    STAGE_ORDER,
    BridgeMode,
    ProviderMode,
    StageName,
    StageStatus,
)

SOURCE_REQUIRED_TEXT = (
    "SOURCE REQUIRED\n"
    "Please upload a conversation/project file or paste the available context.\n"
    "Context Bridge will not invent project state without source material."
)


class UserInput(BaseModel):
    """Raw form input. user_api_key is runtime-only and excluded from dumps."""

    project_name: str | None = None
    bridge_mode: BridgeMode = BridgeMode.STANDARD
    uploaded_source_text: str | None = None
    uploaded_source_filename: str | None = None
    pasted_context: str | None = None
    current_objective: str | None = None
    provider_mode: ProviderMode = ProviderMode.DEMO
    model_name: str | None = None
    base_url: str | None = None
    user_api_key: SecretStr | None = Field(default=None, exclude=True)
    run_live_demo: bool = False
    acknowledge_external_limits: bool = False


class SourcePart(BaseModel):
    label: str
    filename: str | None = None
    content: str
    source_type: str


class SourceBundle(BaseModel):
    """Combined, labeled source material for one run."""

    project_name: str
    bridge_mode: BridgeMode
    source_parts: list[SourcePart]
    current_objective: str
    created_at_runtime: datetime
    usable_source_present: bool

    @classmethod
    def from_user_input(cls, user_input: UserInput) -> "SourceBundle":
        """Combine non-empty source inputs, preserving labels.

        The current objective alone is NOT usable source material (CHP rule:
        empty when both uploaded and pasted source are empty/unusable).
        """
        parts: list[SourcePart] = []
        uploaded = (user_input.uploaded_source_text or "").strip()
        pasted = (user_input.pasted_context or "").strip()
        if uploaded:
            filename = user_input.uploaded_source_filename or "unnamed file"
            parts.append(
                SourcePart(
                    label=f"UPLOADED SOURCE: {filename}",
                    filename=user_input.uploaded_source_filename,
                    content=uploaded,
                    source_type="uploaded_file",
                )
            )
        if pasted:
            parts.append(
                SourcePart(
                    label="PASTED SOURCE",
                    content=pasted,
                    source_type="pasted_text",
                )
            )
        return cls(
            project_name=(user_input.project_name or "").strip() or "Not supplied",
            bridge_mode=user_input.bridge_mode,
            source_parts=parts,
            current_objective=(user_input.current_objective or "").strip()
            or "Not supplied",
            created_at_runtime=datetime.now(UTC),
            usable_source_present=bool(parts),
        )

    def combined_source_text(self) -> str:
        return "\n\n".join(
            f"--- {part.label} ---\n{part.content}" for part in self.source_parts
        )


class StageResult(BaseModel):
    stage_name: StageName
    status: StageStatus = StageStatus.NOT_STARTED
    output_text: str = ""
    parsed_data: dict | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    provider_name: str = ""
    model_name: str = ""
    validation_status: str = "not_validated"


class PipelineRunState(BaseModel):
    """One session's pipeline run. Never contains raw API keys."""

    run_id: str
    mode: ProviderMode
    source_summary: str
    selected_provider_metadata: dict[str, str] = Field(default_factory=dict)
    stage_1_result: StageResult | None = None
    stage_2_result: StageResult | None = None
    stage_3_result: StageResult | None = None
    stage_4a_result: StageResult | None = None
    stage_4b_result: StageResult | None = None
    stage_4c_result: StageResult | None = None
    final_status: str = "not_started"
    external_failures: list[str] = Field(default_factory=list)
    user_visible_warnings: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    _FIELD_BY_STAGE: ClassVar[dict[StageName, str]] = {
        StageName.STAGE_1_LEDGER: "stage_1_result",
        StageName.STAGE_2_DRAFT_CAPSULE: "stage_2_result",
        StageName.STAGE_3_AUDIT: "stage_3_result",
        StageName.STAGE_4A_FINAL_A1: "stage_4a_result",
        StageName.STAGE_4B_FINAL_A2: "stage_4b_result",
        StageName.STAGE_4C_YAML_STATE: "stage_4c_result",
    }

    def set_result(self, result: StageResult) -> None:
        setattr(self, self._FIELD_BY_STAGE[result.stage_name], result)
        self.updated_at = datetime.now(UTC)

    def get_result(self, stage_name: StageName) -> StageResult | None:
        return getattr(self, self._FIELD_BY_STAGE[stage_name])

    def all_results(self) -> list[StageResult]:
        results: list[StageResult] = []
        for stage in STAGE_ORDER:
            result = self.get_result(stage)
            if result is not None:
                results.append(result)
        return results


class FinalOutputs(BaseModel):
    atomic_memory_ledger_md: str = ""
    draft_capsule_md: str = ""
    audit_md: str = ""
    final_pack_a1_md: str = ""
    final_pack_a2_md: str = ""
    yaml_state: str = ""
    combined_bridge_pack_md: str = ""
    resume_prompt: str = ""
    unresolved_confirmations: str = ""
