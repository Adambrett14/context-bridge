"""DemoProvider: replays bundled sample outputs. No network, no key, ever.

The `calls` list doubles as test instrumentation proving the provider is
never invoked on empty source.
"""

from pathlib import Path

from app.domain.enums import ProviderMode, StageName

FIXTURE_FILES: dict[StageName, str] = {
    StageName.STAGE_1_LEDGER: "stage_1_ledger.md",
    StageName.STAGE_2_DRAFT_CAPSULE: "stage_2_draft_capsule.md",
    StageName.STAGE_3_AUDIT: "stage_3_audit.md",
    StageName.STAGE_4A_FINAL_A1: "stage_4a_final_a1.md",
    StageName.STAGE_4B_FINAL_A2: "stage_4b_final_a2.md",
    StageName.STAGE_4C_YAML_STATE: "stage_4c_state.yaml",
}


class DemoProvider:
    """Replays precomputed demo fixtures, clearly labeled as samples in the UI."""

    provider_name = "Demo replay (bundled sample outputs)"
    provider_mode = ProviderMode.DEMO
    model_name = "demo-fixtures"
    credential_source = "none"

    def __init__(self, demo_outputs_dir: Path) -> None:
        self._dir = demo_outputs_dir
        self.calls: list[StageName] = []

    def generate_stage_output(
        self,
        stage_name: StageName,
        assembled_prompt: str,
        run_metadata: dict[str, str],
    ) -> str:
        self.calls.append(stage_name)
        return (self._dir / FIXTURE_FILES[stage_name]).read_text(encoding="utf-8")
