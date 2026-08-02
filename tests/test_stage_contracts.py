"""Contracts: full stage coverage, tokens present in templates, headings sane."""

from pathlib import Path

from app.domain.enums import STAGE_ORDER, StageName
from app.domain.stage_contracts import CONTRACTS

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "app" / "prompts"


def test_every_stage_has_a_contract() -> None:
    assert set(CONTRACTS) == set(STAGE_ORDER)


def test_templates_contain_every_required_token() -> None:
    for contract in CONTRACTS.values():
        template = (PROMPTS_DIR / contract.prompt_filename).read_text(
            encoding="utf-8"
        )
        for token in contract.required_tokens:
            assert token in template, f"{contract.prompt_filename} missing {token}"


def test_non_yaml_stages_declare_headings() -> None:
    for stage, contract in CONTRACTS.items():
        if stage is StageName.STAGE_4C_YAML_STATE:
            assert contract.is_yaml
            assert not contract.required_headings
        else:
            assert contract.required_headings
