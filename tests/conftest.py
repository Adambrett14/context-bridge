"""Shared test helpers: paths and a scriptable FakeProvider (no network)."""

from collections.abc import Callable
from pathlib import Path

from app.domain.enums import ProviderMode, StageName
from app.infrastructure.providers.demo_provider import FIXTURE_FILES

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "app"
DEMO_OUTPUTS_DIR = APP_DIR / "samples" / "demo_outputs"

Script = Callable[[StageName, str, dict[str, str]], str]


class FakeProvider:
    """Scriptable provider for orchestration tests."""

    provider_name = "Fake provider (tests)"
    provider_mode = ProviderMode.BYOK_OPENAI_COMPATIBLE
    model_name = "fake-model"
    credential_source = "runtime_user_key"

    def __init__(self, script: Script) -> None:
        self._script = script
        self.calls: list[tuple[StageName, str]] = []

    def generate_stage_output(
        self,
        stage_name: StageName,
        assembled_prompt: str,
        run_metadata: dict[str, str],
    ) -> str:
        self.calls.append((stage_name, assembled_prompt))
        return self._script(stage_name, assembled_prompt, run_metadata)


def fixture_output(stage: StageName) -> str:
    return (DEMO_OUTPUTS_DIR / FIXTURE_FILES[stage]).read_text(encoding="utf-8")
