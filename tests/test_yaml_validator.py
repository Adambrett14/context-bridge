"""YAML validator: fixture passes; broken inputs fail with clear problems."""

from pathlib import Path

from app.application.yaml_validator import validate_yaml_state

FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "app"
    / "samples"
    / "demo_outputs"
    / "stage_4c_state.yaml"
)


def test_demo_fixture_is_valid() -> None:
    assert validate_yaml_state(FIXTURE.read_text(encoding="utf-8")) == []


def test_unparseable_yaml_fails() -> None:
    problems = validate_yaml_state("context_bridge: [unclosed")
    assert problems
    assert "parse error" in problems[0].lower()


def test_missing_root_key_fails() -> None:
    problems = validate_yaml_state("something_else:\n  project: 'X'\n")
    assert problems == ["missing root key: context_bridge"]


def test_missing_required_fields_fail() -> None:
    problems = validate_yaml_state("context_bridge:\n  project: 'X'\n")
    assert problems
    assert "missing keys" in problems[0]
