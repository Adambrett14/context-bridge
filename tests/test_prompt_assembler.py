"""Prompt assembly: token replacement completeness and correct injection."""

from pathlib import Path

from app.application.prompt_assembler import PromptAssembler
from app.domain.enums import STAGE_ORDER, StageName
from app.domain.models import SourceBundle, UserInput

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "app" / "prompts"

DUMMY_OUTPUTS = {
    StageName.STAGE_1_LEDGER: "LEDGER-BODY",
    StageName.STAGE_2_DRAFT_CAPSULE: "DRAFT-BODY",
    StageName.STAGE_3_AUDIT: "AUDIT-BODY",
}


def make_bundle() -> SourceBundle:
    return SourceBundle.from_user_input(
        UserInput(
            project_name="Test Project",
            pasted_context="[M01] USER: hello world",
            current_objective="Finish the widget",
        )
    )


def test_no_tokens_remain_after_assembly() -> None:
    assembler = PromptAssembler(PROMPTS_DIR)
    for stage in STAGE_ORDER:
        prompt = assembler.assemble(stage, make_bundle(), DUMMY_OUTPUTS)
        assert "{{" not in prompt, f"unreplaced token in {stage.value}"


def test_stage_1_prompt_contains_source_and_metadata() -> None:
    assembler = PromptAssembler(PROMPTS_DIR)
    prompt = assembler.assemble(StageName.STAGE_1_LEDGER, make_bundle(), {})
    assert "hello world" in prompt
    assert "Test Project" in prompt
    assert "Standard" in prompt
    assert "PASTED SOURCE" in prompt


def test_downstream_prompts_receive_prior_outputs() -> None:
    assembler = PromptAssembler(PROMPTS_DIR)
    audit = assembler.assemble(StageName.STAGE_3_AUDIT, make_bundle(), DUMMY_OUTPUTS)
    assert "LEDGER-BODY" in audit
    assert "DRAFT-BODY" in audit
    yaml_prompt = assembler.assemble(
        StageName.STAGE_4C_YAML_STATE, make_bundle(), DUMMY_OUTPUTS
    )
    assert "DRAFT-BODY" in yaml_prompt
    assert "AUDIT-BODY" in yaml_prompt
