"""Assemble stage prompts from versioned templates.

Injects project metadata, source, rules, schema, and prior stage outputs.
Has no access to API keys by construction — credentials never enter prompts.
"""

from pathlib import Path

from app.domain.enums import StageName
from app.domain.models import SourceBundle
from app.domain.stage_contracts import CONTRACTS


class PromptAssembler:
    def __init__(self, prompts_dir: Path) -> None:
        self._dir = prompts_dir
        self._cache: dict[str, str] = {}

    def _asset(self, filename: str) -> str:
        if filename not in self._cache:
            self._cache[filename] = (self._dir / filename).read_text(encoding="utf-8")
        return self._cache[filename]

    def assemble(
        self,
        stage_name: StageName,
        bundle: SourceBundle,
        stage_outputs: dict[StageName, str],
    ) -> str:
        contract = CONTRACTS[stage_name]
        prompt = self._asset(contract.prompt_filename)
        replacements: dict[str, str] = {
            "{{BRIDGE_RULES}}": self._asset("bridge_rules.md"),
            "{{GOVERNANCE_RULES}}": self._asset("governance_rules.md"),
            "{{CAPSULE_SCHEMA}}": self._asset("capsule_schema.md"),
            "{{PROJECT_NAME}}": bundle.project_name,
            "{{BRIDGE_MODE}}": bundle.bridge_mode.value,
            "{{CURRENT_OBJECTIVE}}": bundle.current_objective,
            "{{SOURCE_BUNDLE}}": bundle.combined_source_text(),
            "{{LEDGER}}": stage_outputs.get(StageName.STAGE_1_LEDGER, ""),
            "{{DRAFT_CAPSULE}}": stage_outputs.get(
                StageName.STAGE_2_DRAFT_CAPSULE, ""
            ),
            "{{AUDIT}}": stage_outputs.get(StageName.STAGE_3_AUDIT, ""),
        }
        for token, value in replacements.items():
            prompt = prompt.replace(token, value)
        return prompt
