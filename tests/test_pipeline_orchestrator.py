"""Demo pipeline end-to-end: completion, ordering, validation, combined exports."""

from pathlib import Path

from app.application.export_builder import build_final_outputs
from app.application.pipeline_orchestrator import PipelineOrchestrator
from app.application.prompt_assembler import PromptAssembler
from app.domain.enums import STAGE_ORDER, StageStatus
from app.domain.models import SourceBundle, UserInput
from app.infrastructure.providers.demo_provider import DemoProvider

APP_DIR = Path(__file__).resolve().parent.parent / "app"


def run_demo() -> tuple[DemoProvider, object]:
    transcript = (APP_DIR / "samples" / "demo_transcript.md").read_text(
        encoding="utf-8"
    )
    bundle = SourceBundle.from_user_input(
        UserInput(project_name="Trailhead Tracker", pasted_context=transcript)
    )
    provider = DemoProvider(APP_DIR / "samples" / "demo_outputs")
    orchestrator = PipelineOrchestrator(provider, PromptAssembler(APP_DIR / "prompts"))
    return provider, orchestrator.run(bundle)


def test_demo_pipeline_completes_all_stages() -> None:
    _, state = run_demo()
    assert state.final_status == "complete"
    results = state.all_results()
    assert len(results) == len(STAGE_ORDER)
    for result in results:
        assert result.status is StageStatus.COMPLETE
        assert result.validation_status == "passed"


def test_provider_called_in_canonical_stage_order() -> None:
    provider, _ = run_demo()
    assert provider.calls == list(STAGE_ORDER)


def test_final_outputs_combine_correctly() -> None:
    _, state = run_demo()
    outputs = build_final_outputs(state)
    assert "# CONTEXT BRIDGE — FULL BRIDGE PACK" in outputs.combined_bridge_pack_md
    assert "(Sections 1-10)" in outputs.combined_bridge_pack_md
    assert "(Sections 11-19)" in outputs.combined_bridge_pack_md
    assert outputs.resume_prompt.startswith("Treat the pasted Context Bridge capsule")
    assert "Does desktop-priority" in outputs.unresolved_confirmations
