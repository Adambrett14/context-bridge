"""Sequential pipeline orchestrator with live-provider support.

M3: classified provider errors (already redacted upstream), repair/retry
for malformed output, adaptive chunk-and-merge for Stage 1, progress
callbacks, honest failure states. No app-defined size caps anywhere.
"""

import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from app.application.chunk_coordinator import (
    DEFAULT_CHUNK_THRESHOLD_CHARS,
    merge_ledgers,
    split_into_chunks,
)
from app.application.output_validator import validate_stage_output
from app.application.prompt_assembler import PromptAssembler
from app.application.yaml_validator import validate_yaml_state
from app.domain.enums import (
    STAGE_ORDER,
    ErrorCategory,
    StageName,
    StageStatus,
)
from app.domain.errors import ProviderCallError
from app.domain.models import (
    SOURCE_REQUIRED_TEXT,
    PipelineRunState,
    SourceBundle,
    SourcePart,
    StageResult,
)
from app.infrastructure.providers.base import Provider

FAILED_STATUS_BY_CATEGORY: dict[ErrorCategory, str] = {
    ErrorCategory.AUTH_ERROR: "failed_auth",
    ErrorCategory.PROVIDER_LIMIT_ERROR: "failed_external_limit",
    ErrorCategory.TIMEOUT: "failed_external_limit",
    ErrorCategory.HOST_LIMIT_ERROR: "failed_external_limit",
    ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE: "failed_external_limit",
    ErrorCategory.MALFORMED_MODEL_OUTPUT: "failed_validation",
}

EXTERNAL_CATEGORIES = frozenset(
    {
        ErrorCategory.PROVIDER_LIMIT_ERROR,
        ErrorCategory.TIMEOUT,
        ErrorCategory.HOST_LIMIT_ERROR,
        ErrorCategory.EXTERNAL_PROVIDER_UNAVAILABLE,
    }
)


class PipelineOrchestrator:
    """Runs the six Context Bridge stages in order and records results."""

    def __init__(
        self,
        provider: Provider,
        assembler: PromptAssembler,
        *,
        chunk_threshold_chars: int = DEFAULT_CHUNK_THRESHOLD_CHARS,
        max_repair_attempts: int = 1,
        on_stage_start: Callable[[StageName], None] | None = None,
        on_stage_complete: Callable[[StageResult], None] | None = None,
    ) -> None:
        self._provider = provider
        self._assembler = assembler
        self._chunk_threshold = chunk_threshold_chars
        self._max_repairs = max_repair_attempts
        self._on_start = on_stage_start
        self._on_complete = on_stage_complete
        self._last_error_category: ErrorCategory | None = None

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
            if self._on_start is not None:
                self._on_start(stage)
            if stage is StageName.STAGE_1_LEDGER:
                result = self._run_stage_1(bundle, stage_outputs, state)
            else:
                result = self._run_stage(stage, bundle, stage_outputs)
            state.set_result(result)
            if self._on_complete is not None:
                self._on_complete(result)
            if result.status is not StageStatus.COMPLETE:
                if (
                    self._last_error_category in EXTERNAL_CATEGORIES
                    and result.errors
                ):
                    state.external_failures.append(result.errors[0])
                state.final_status = self._failure_status(result)
                return state
        state.final_status = "complete"
        return state

    def _failure_status(self, result: StageResult) -> str:
        if self._last_error_category is not None:
            return FAILED_STATUS_BY_CATEGORY.get(
                self._last_error_category, "failed_unknown"
            )
        if result.validation_status == "failed":
            return "failed_validation"
        return "failed_unknown"

    def _validate(self, stage: StageName, output: str) -> list[str]:
        if stage is StageName.STAGE_4C_YAML_STATE:
            return validate_yaml_state(output)
        return validate_stage_output(stage, output)

    def _generate_with_repair(
        self, stage: StageName, prompt: str
    ) -> tuple[str, list[str], int]:
        output = self._provider.generate_stage_output(
            stage, prompt, {"stage": stage.value}
        )
        problems = self._validate(stage, output)
        repairs = 0
        while problems and repairs < self._max_repairs:
            repairs += 1
            repair_prompt = (
                f"{prompt}\n\n## REPAIR INSTRUCTION\n"
                "Your previous output failed validation:\n- "
                + "\n- ".join(problems)
                + "\nOutput the ENTIRE corrected response again, following "
                "the required output format exactly. Do not add commentary."
            )
            output = self._provider.generate_stage_output(
                stage,
                repair_prompt,
                {"stage": stage.value, "repair_attempt": str(repairs)},
            )
            problems = self._validate(stage, output)
        return output, problems, repairs

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
        self._last_error_category = None
        try:
            prompt = self._assembler.assemble(stage, bundle, stage_outputs)
            output, problems, repairs = self._generate_with_repair(stage, prompt)
        except ProviderCallError as exc:
            self._last_error_category = exc.category
            result.status = StageStatus.FAILED
            result.errors = [exc.message]
            result.validation_status = "provider_error"
            result.completed_at = datetime.now(UTC)
            return result
        except Exception as exc:
            result.status = StageStatus.FAILED
            result.errors = [f"{type(exc).__name__} during stage execution"]
            result.completed_at = datetime.now(UTC)
            return result
        result.output_text = output
        if repairs:
            result.warnings.append(
                f"required {repairs} repair attempt(s) to pass validation"
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

    def _run_stage_1(
        self,
        bundle: SourceBundle,
        stage_outputs: dict[StageName, str],
        state: PipelineRunState,
    ) -> StageResult:
        full_text = bundle.combined_source_text()
        chunks = split_into_chunks(full_text, self._chunk_threshold)
        if len(chunks) == 1:
            result = self._run_stage(
                StageName.STAGE_1_LEDGER, bundle, stage_outputs
            )
            if (
                result.status is StageStatus.FAILED
                and self._last_error_category
                is ErrorCategory.PROVIDER_LIMIT_ERROR
            ):
                retry_chunks = split_into_chunks(
                    full_text, max(self._chunk_threshold // 2, 1_000)
                )
                if len(retry_chunks) > 1:
                    state.user_visible_warnings.append(
                        "Provider rejected the full source as submitted; "
                        "retried with adaptive chunking (external "
                        "constraint, not an app cap)."
                    )
                    return self._run_stage_1_chunked(
                        bundle, retry_chunks, stage_outputs
                    )
            return result
        state.user_visible_warnings.append(
            f"Large source split into {len(chunks)} chunks by adaptive "
            "chunking; no content dropped, no app-defined cap applied."
        )
        return self._run_stage_1_chunked(bundle, chunks, stage_outputs)

    def _run_stage_1_chunked(
        self,
        bundle: SourceBundle,
        chunks: list[str],
        stage_outputs: dict[StageName, str],
    ) -> StageResult:
        result = StageResult(
            stage_name=StageName.STAGE_1_LEDGER,
            status=StageStatus.RUNNING,
            started_at=datetime.now(UTC),
            provider_name=self._provider.provider_name,
            model_name=self._provider.model_name,
        )
        self._last_error_category = None
        total = len(chunks)
        chunk_outputs: list[str] = []
        failures: list[str] = []
        for index, chunk in enumerate(chunks, start=1):
            chunk_bundle = bundle.model_copy(
                update={
                    "source_parts": [
                        SourcePart(
                            label=f"SOURCE CHUNK {index} OF {total}",
                            content=chunk,
                            source_type="chunk",
                        )
                    ]
                }
            )
            prompt = self._assembler.assemble(
                StageName.STAGE_1_LEDGER, chunk_bundle, {}
            )
            try:
                output, problems, repairs = self._generate_with_repair(
                    StageName.STAGE_1_LEDGER, prompt
                )
            except ProviderCallError as exc:
                self._last_error_category = exc.category
                failures.append(f"chunk {index} of {total}: {exc.message}")
                continue
            if repairs:
                result.warnings.append(
                    f"chunk {index}: {repairs} repair attempt(s)"
                )
            if problems:
                failures.append(
                    f"chunk {index} of {total} failed validation: "
                    + "; ".join(problems)
                )
            else:
                chunk_outputs.append(output)
        merged = merge_ledgers(chunk_outputs) if chunk_outputs else ""
        if failures:
            result.status = StageStatus.FAILED
            result.errors = failures
            result.validation_status = "failed"
            failure_report = "# CHUNK FAILURES\n- " + "\n- ".join(failures)
            result.output_text = (
                f"{merged}\n\n{failure_report}" if merged else failure_report
            )
        else:
            result.status = StageStatus.COMPLETE
            result.validation_status = "passed"
            result.output_text = merged
            stage_outputs[StageName.STAGE_1_LEDGER] = merged
        result.completed_at = datetime.now(UTC)
        return result
