"""Chunk coordinator: soft splitting preserves everything; merge is complete."""

from app.application.chunk_coordinator import merge_ledgers, split_into_chunks
from app.domain.stage_contracts import STAGE_1_HEADINGS

LEDGER_TEMPLATE = """# SOURCE CHECK
chunk source ok
# EPISODE MAP
- episode
# ATOMIC MEMORY LEDGER
| ID | Class | Statement | Status | Confidence | Source | Notes |
|---|---|---|---|---|---|---|
| R1 | fact | {statement} | active | confirmed | T01 | note |
# CONFLICTS AND POSSIBLE SUPERSESSION
None identified.
# ARTIFACT REGISTER
None identified.
# MISSING OR UNCERTAIN INFORMATION
None identified.
# SENSITIVE OR EXCLUDED INFORMATION
None identified.
# HANDOFF PRIORITIES
1. continue
"""


def test_small_input_single_chunk() -> None:
    assert split_into_chunks("short text", 1_000) == ["short text"]


def test_paragraphs_preserved_across_chunks() -> None:
    paragraphs = [f"Paragraph {i}: " + "x" * 90 for i in range(10)]
    text = "\n\n".join(paragraphs)
    chunks = split_into_chunks(text, 250)
    assert len(chunks) > 1
    for paragraph in paragraphs:
        assert sum(chunk.count(paragraph) for chunk in chunks) == 1


def test_oversize_paragraph_hard_split_preserves_content() -> None:
    text = "y" * 10_000
    chunks = split_into_chunks(text, 3_000)
    assert all(len(chunk) <= 3_000 for chunk in chunks)
    assert "".join(chunks) == text


def test_merge_produces_headings_and_chunk_markers() -> None:
    merged = merge_ledgers(
        [
            LEDGER_TEMPLATE.format(statement="alpha finding"),
            LEDGER_TEMPLATE.format(statement="beta finding"),
        ]
    )
    for heading in STAGE_1_HEADINGS:
        assert heading in merged
    assert "**[Chunk 1 of 2]**" in merged
    assert "**[Chunk 2 of 2]**" in merged
    assert "alpha finding" in merged
    assert "beta finding" in merged
    assert "Merge note" not in merged
    duplicated = merge_ledgers(
        [
            LEDGER_TEMPLATE.format(statement="same finding"),
            LEDGER_TEMPLATE.format(statement="same finding"),
        ]
    )
    assert "Merge note" in duplicated
