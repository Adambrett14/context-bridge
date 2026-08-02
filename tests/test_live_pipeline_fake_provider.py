"""Live-path orchestration with FakeProvider: order, repair, failure, no caps."""


from app.application.pipeline_orchestrator import PipelineOrchestrator
from app.application.prompt_assembler import PromptAssembler
from app.domain.enums import STAGE_ORDER, ErrorCategory, StageName
from app.domain.errors import ProviderCallError
from app.domain.models import SourceBundle, UserInput
from tests.conftest import APP_DIR, FakeProvider, fixture_output

PROMPTS_DIR = APP_DIR / "prompts"


def make_bundle(text: str = "") -> SourceBundle:
    if not text:
        text = (APP_DIR / "samples" / "demo_transcript.md").read_text(
            encoding="utf-8"
        )
    return SourceBundle.from_user_input(
        UserInput(project_name="Test", pasted_context=text)
    )


def make_orchestrator(provider: FakeProvider, **kwargs) -> PipelineOrchestrator:
    return PipelineOrchestrator(provider, PromptAssembler(PROMPTS_DIR), **kwargs)


def test_stages_called_in_order_and_complete() -> None:
    provider = FakeProvider(lambda stage, prompt, meta: fixture_output(stage))
    state = make_orchestrator(provider).run(make_bundle())
    assert state.final_status == "complete"
    assert [stage for stage, _ in provider.calls] == list(STAGE_ORDER)


def test_malformed_yaml_repaired_once_then_completes() -> None:
    yaml_calls = {"count": 0}

    def script(stage: StageName, prompt: str, meta: dict[str, str]) -> str:
        if stage is StageName.STAGE_4C_YAML_STATE:
            yaml_calls["count"] += 1
            if yaml_calls["count"] == 1:
                return "not: [valid yaml"
        return fixture_output(stage)

    provider = FakeProvider(script)
    state = make_orchestrator(provider).run(make_bundle())
    assert state.final_status == "complete"
    assert yaml_calls["count"] == 2
    repair_prompts = [
        prompt
        for stage, prompt in provider.calls
        if stage is StageName.STAGE_4C_YAML_STATE
    ]
    assert "REPAIR INSTRUCTION" in repair_prompts[1]
    assert state.stage_4c_result is not None
    assert state.stage_4c_result.warnings


def test_unrepairable_output_fails_validation_with_partial_download() -> None:
    def script(stage: StageName, prompt: str, meta: dict[str, str]) -> str:
        if stage is StageName.STAGE_1_LEDGER:
            return "totally wrong output"
        return fixture_output(stage)

    provider = FakeProvider(script)
    state = make_orchestrator(provider).run(make_bundle())
    assert state.final_status == "failed_validation"
    stage_1_calls = [
        stage for stage, _ in provider.calls if stage is StageName.STAGE_1_LEDGER
    ]
    assert len(stage_1_calls) == 2  # original + one repair attempt
    assert state.stage_1_result is not None
    assert state.stage_1_result.output_text == "totally wrong output"
    assert any("missing required heading" in e for e in state.stage_1_result.errors)


def test_giant_input_is_chunked_not_refused() -> None:
    provider = FakeProvider(lambda stage, prompt, meta: fixture_output(stage))
    giant = "\n\n".join(
        f"Paragraph {i}: " + "x" * 1_000 for i in range(400)
    )
    state = make_orchestrator(provider).run(make_bundle(giant))
    assert state.final_status == "complete"
    stage_1_calls = [
        stage for stage, _ in provider.calls if stage is StageName.STAGE_1_LEDGER
    ]
    assert len(stage_1_calls) > 1
    assert any("adaptive chunking" in w for w in state.user_visible_warnings)
    assert state.stage_1_result is not None
    assert "[Chunk 1 of" in state.stage_1_result.output_text


def test_auth_failure_sets_failed_auth_and_stays_redacted() -> None:
    def script(stage: StageName, prompt: str, meta: dict[str, str]) -> str:
        raise ProviderCallError(
            "The provider rejected the credentials. Re-enter the key or "
            "provider settings. Your key was not saved by Context Bridge.",
            ErrorCategory.AUTH_ERROR,
        )

    provider = FakeProvider(script)
    state = make_orchestrator(provider).run(make_bundle())
    assert state.final_status == "failed_auth"
    assert state.stage_1_result is not None
    assert "credentials" in state.stage_1_result.errors[0]
    assert "sk-" not in state.model_dump_json()
