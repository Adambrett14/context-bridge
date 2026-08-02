"""Validate stage outputs against contracts: headings, tables, final notice.

Headings are matched literally (they are single-line constructs). The final
notice is prose and may line-wrap anywhere, so it is checked against a
whitespace-normalized copy of the output.
"""

from app.domain.enums import StageName
from app.domain.stage_contracts import CONTRACTS, FINAL_NOTICE_SNIPPET


def is_source_required(output_text: str) -> bool:
    return output_text.strip().startswith("SOURCE REQUIRED")


def validate_stage_output(stage_name: StageName, output_text: str) -> list[str]:
    """Return a list of validation problems; an empty list means valid."""
    contract = CONTRACTS[stage_name]
    problems: list[str] = []
    if contract.is_yaml:
        return problems  # Stage 4C is handled by yaml_validator.
    for heading in contract.required_headings:
        if heading not in output_text:
            problems.append(f"missing required heading: {heading}")
    if contract.requires_markdown_table and "|" not in output_text:
        problems.append("missing required markdown table")
    if stage_name is StageName.STAGE_4B_FINAL_A2:
        normalized = " ".join(output_text.split())
        if FINAL_NOTICE_SNIPPET not in normalized:
            problems.append("missing final not-stored notice")
    return problems
