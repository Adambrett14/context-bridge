"""M1 smoke tests: skeleton assets exist, fixtures load, secrets template is clean."""

import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"

PROMPT_FILES = [
    "bridge_rules.md",
    "governance_rules.md",
    "capsule_schema.md",
    "stage_1_atomic_memory_ledger.md",
    "stage_2_draft_capsule.md",
    "stage_3_capsule_audit.md",
    "stage_4a_final_bridge_pack_a1.md",
    "stage_4b_final_bridge_pack_a2.md",
    "stage_4c_machine_readable_state.md",
]

DEMO_FILES = [
    "demo_transcript.md",
    "demo_outputs/stage_1_ledger.md",
    "demo_outputs/stage_2_draft_capsule.md",
    "demo_outputs/stage_3_audit.md",
    "demo_outputs/stage_4a_final_a1.md",
    "demo_outputs/stage_4b_final_a2.md",
    "demo_outputs/stage_4c_state.yaml",
]

REQUIRED_YAML_KEYS = {
    "metadata",
    "project",
    "current_objective",
    "confirmed_requirements",
    "rejected_and_superseded_directions",
    "verification_status",
    "resume_instruction",
}


def test_prompt_assets_exist_and_are_nonempty() -> None:
    for name in PROMPT_FILES:
        path = APP / "prompts" / name
        assert path.is_file(), f"missing prompt asset: {name}"
        assert path.stat().st_size > 0, f"empty prompt asset: {name}"


def test_demo_fixtures_exist_and_are_nonempty() -> None:
    for name in DEMO_FILES:
        path = APP / "samples" / name
        assert path.is_file(), f"missing demo fixture: {name}"
        assert path.stat().st_size > 0, f"empty demo fixture: {name}"


def test_demo_yaml_fixture_parses_with_required_keys() -> None:
    raw = (APP / "samples" / "demo_outputs" / "stage_4c_state.yaml").read_text(
        encoding="utf-8"
    )
    data = yaml.safe_load(raw)
    assert isinstance(data, dict) and "context_bridge" in data
    missing = REQUIRED_YAML_KEYS - set(data["context_bridge"])
    assert not missing, f"YAML fixture missing keys: {missing}"


def test_secrets_template_contains_no_real_values() -> None:
    raw = (ROOT / ".streamlit" / "secrets.toml.example").read_bytes()
    data = tomllib.loads(raw.decode("utf-8"))
    assert data["OWNER_PROVIDER_ENABLED"] is False
    assert data["OWNER_PROVIDER_API_KEY"] == ""
    assert data["OWNER_MODE_PASSPHRASE"] == ""
