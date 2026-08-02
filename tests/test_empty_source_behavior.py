"""Empty source: SOURCE REQUIRED output, and the provider is never called."""

from pathlib import Path

from app.application.pipeline_orchestrator import PipelineOrchestrator
from app.application.prompt_assembler import PromptAssembler
from app.domain.models import SourceBundle, UserInput
from app.infrastructure.providers.demo_provider import DemoProvider

APP_DIR = Path(__file__).resolve().parent.parent / "app"


def run_with(user_input: UserInput) -> tuple[DemoProvider, object]:
    provider = DemoProvider(APP_DIR / "samples" / "demo_outputs")
    orchestrator = PipelineOrchestrator(provider, PromptAssembler(APP_DIR / "prompts"))
    return provider, orchestrator.run(SourceBundle.from_user_input(user_input))


def test_no_source_returns_source_required() -> None:
    provider, state = run_with(UserInput())
    assert state.final_status == "source_required"
    assert state.stage_1_result is not None
    assert state.stage_1_result.output_text.startswith("SOURCE REQUIRED")
    assert provider.calls == []


def test_whitespace_only_source_is_not_usable() -> None:
    provider, state = run_with(UserInput(pasted_context="   \n\t  "))
    assert state.final_status == "source_required"
    assert provider.calls == []


def test_objective_alone_is_not_source() -> None:
    provider, state = run_with(UserInput(current_objective="Ship it"))
    assert state.final_status == "source_required"
    assert provider.calls == []
