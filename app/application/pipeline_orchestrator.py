"""Sequential pipeline orchestrator: Stage 1 → 4C against any Provider.

M2 scope: run, validate, record, stop on SOURCE REQUIRED or validation
failure. Repair/retry and classified external-error mapping arrive in M3.
Exception text is deliberately reduced to the exception type so provider
errors can never leak credentials into results.
"""

import uuid
from datetime import UTC, datetime

from app.application.output_validator import validate_stage_output
from app.application.prompt_assembler import PromptAssembler
from app.application.yaml_validator import validate_yaml_state
from app.domain.enums import STAGE_ORDER, StageName, StageStatus
from app.domain.models import (
    SOURCE_REQUIRED_TEXT,
    PipelineRunState,
    SourceBundle,
    StageResult,
)
from app.infrastructure.providers.base import Provider


class PipelineOrchestrator:
    """Runs the six Context Bridge stages in order and records results."""

    def __init__(self, provider: Provider, assembler: PromptAssembler) -> None:
        self._provider = provider
        self._assembler = assembler

    def run(self, bundle: SourceBundle) -> PipelineRunState:
        now = datetime.now(UTC)
        state = PipelineRunState(
            run_id=uuid.uuid4().hex[:12],
            mode=self._provider.provider_mode,
            source_summary=(
                f"{len(bundle.source_parts)} source part(s); "
                f"project: {bundle.project_name}"
            ),
            selected_provider_metadata={
                "provider_name": self._provider.provider_name,
                "model_name": self._provider.model_name,
                "credential_source": self._provider.credential_source,
            },
            created_at=now,
            updated_at=now,
        )
        if not bundle.usable_source_present:
            state.set_result(
                StageResult(
                    stage_name=StageName.STAGE_1_LEDGER,
                    status=StageStatus.FAILED,
                    output_text=SOURCE_REQUIRED_TEXT,
                    errors=["source_required"],
                    validation_status="source_required",
                )
            )
            state.final_status = "source_required"
            return state

        stage_outputs: dict[StageName, str] = {}
        for stage in STAGE_ORDER:
            result = self._run_stage(stage, bundle, stage_outputs)
            state.set_result(result)
            if result.status is not StageStatus.COMPLETE:
                state.final_status = "failed_validation"
                return state
        state.final_status = "complete"
        return state

    def _run_stage(
        self,
        stage: StageName,
        bundle: SourceBundle,
        stage_outputs: dict[StageName, str],
    ) -> StageResult:
        result = StageResult(
            stage_name=stage,
            status=StageStatus.RUNNING,
            started_at=datetime.now(UTC),
            provider_name=self._provider.provider_name,
            model_name=self._provider.model_name,
        )
        try:
            prompt = self._assembler.assemble(stage, bundle, stage_outputs)
            output = self._provider.generate_stage_output(
                stage, prompt, {"stage": stage.value}
            )
        except Exception as exc:  # M3 replaces with classified error mapping.
            result.status = StageStatus.FAILED
            result.errors = [f"{type(exc).__name__} during stage execution"]
            result.completed_at = datetime.now(UTC)
            return result
        result.output_text = output
        problems = (
            validate_yaml_state(output)
            if stage is StageName.STAGE_4C_YAML_STATE
            else validate_stage_output(stage, output)
        )
        if problems:
            result.status = StageStatus.FAILED
            result.errors = problems
            result.validation_status = "failed"
        else:
            result.status = StageStatus.COMPLETE
            result.validation_status = "passed"
            stage_outputs[stage] = output
        result.completed_at = datetime.now(UTC)
        return result
