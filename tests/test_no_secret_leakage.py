"""Secrets never reach dumps, run state, or exports."""

from pathlib import Path

from pydantic import SecretStr

from app.application.export_builder import build_final_outputs
from app.application.pipeline_orchestrator import PipelineOrchestrator
from app.application.prompt_assembler import PromptAssembler
from app.domain.models import SourceBundle, UserInput
from app.infrastructure.providers.demo_provider import DemoProvider

APP_DIR = Path(__file__).resolve().parent.parent / "app"
FAKE_KEY = "sk-FAKE-super-secret-123"


def make_input() -> UserInput:
    transcript = (APP_DIR / "samples" / "demo_transcript.md").read_text(
        encoding="utf-8"
    )
    return UserInput(
        project_name="Trailhead Tracker",
        pasted_context=transcript,
        user_api_key=SecretStr(FAKE_KEY),
    )


def test_model_dump_excludes_api_key() -> None:
    dumped = str(make_input().model_dump())
    assert FAKE_KEY not in dumped
    assert "user_api_key" not in dumped


def test_repr_masks_api_key() -> None:
    assert FAKE_KEY not in repr(make_input())


def test_run_state_and_exports_contain_no_key_material() -> None:
    bundle = SourceBundle.from_user_input(make_input())
    provider = DemoProvider(APP_DIR / "samples" / "demo_outputs")
    orchestrator = PipelineOrchestrator(provider, PromptAssembler(APP_DIR / "prompts"))
    state = orchestrator.run(bundle)
    assert FAKE_KEY not in state.model_dump_json()
    outputs = build_final_outputs(state)
    for text in outputs.model_dump().values():
        assert FAKE_KEY not in text
