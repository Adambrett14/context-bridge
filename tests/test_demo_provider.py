"""DemoProvider: replays bundled fixtures and records calls. No network."""

from pathlib import Path

from app.domain.enums import STAGE_ORDER
from app.infrastructure.providers.demo_provider import FIXTURE_FILES, DemoProvider

DEMO_OUTPUTS_DIR = (
    Path(__file__).resolve().parent.parent / "app" / "samples" / "demo_outputs"
)


def test_returns_bundled_fixture_for_every_stage() -> None:
    provider = DemoProvider(DEMO_OUTPUTS_DIR)
    for stage in STAGE_ORDER:
        output = provider.generate_stage_output(stage, "prompt", {})
        expected = (DEMO_OUTPUTS_DIR / FIXTURE_FILES[stage]).read_text(
            encoding="utf-8"
        )
        assert output == expected


def test_records_stage_calls_in_order() -> None:
    provider = DemoProvider(DEMO_OUTPUTS_DIR)
    for stage in STAGE_ORDER:
        provider.generate_stage_output(stage, "prompt", {})
    assert provider.calls == list(STAGE_ORDER)
