"""Adaptive chunk-and-merge for large sources (CHP large-input strategy).

The threshold is SOFT: bigger inputs are split, never refused. Splitting
respects paragraph boundaries; an oversize single paragraph is hard-split
with zero content loss. Merging preserves every chunk ledger under the
required headings and reports (never deletes) suspected duplicates.
"""

from app.domain.stage_contracts import STAGE_1_HEADINGS

DEFAULT_CHUNK_THRESHOLD_CHARS = 60_000  # soft, user-adjustable; not a cap


def split_into_chunks(text: str, threshold: int) -> list[str]:
    """Split text into chunks of at most `threshold` chars, preserving order
    and every character of content."""
    if threshold < 1:
        threshold = 1
    if len(text) <= threshold:
        return [text]
    chunks: list[str] = []
    current = ""
    for paragraph in text.split("\n\n"):
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= threshold:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        if len(paragraph) <= threshold:
            current = paragraph
        else:
            for start in range(0, len(paragraph), threshold):
                piece = paragraph[start : start + threshold]
                if len(piece) == threshold:
                    chunks.append(piece)
                else:
                    current = piece
    if current:
        chunks.append(current)
    return chunks


def _split_sections(ledger_md: str) -> dict[str, str]:
    bodies: dict[str, list[str]] = {h: [] for h in STAGE_1_HEADINGS}
    current: str | None = None
    for line in ledger_md.splitlines():
        stripped = line.strip()
        if stripped in bodies:
            current = stripped
            continue
        if current is not None:
            bodies[current].append(line)
    return {h: "\n".join(lines).strip() for h, lines in bodies.items()}


def _statements(section_bodies: dict[str, str]) -> list[str]:
    statements: list[str] = []
    for row in section_bodies["# ATOMIC MEMORY LEDGER"].splitlines():
        cells = row.split("|")
        if len(cells) > 4:
            statement = cells[3].strip()
            if statement and statement != "Statement" and "---" not in statement:
                statements.append(statement)
    return statements


def merge_ledgers(chunk_outputs: list[str]) -> str:
    """Merge per-chunk Stage 1 ledgers into one ledger with all required
    headings. Nothing is dropped; suspected duplicates are reported."""
    count = len(chunk_outputs)
    if count == 1:
        return chunk_outputs[0]
    per_chunk = [_split_sections(output) for output in chunk_outputs]
    seen: set[str] = set()
    duplicates = 0
    for sections in per_chunk:
        for statement in _statements(sections):
            if statement in seen:
                duplicates += 1
            seen.add(statement)
    parts: list[str] = []
    for heading in STAGE_1_HEADINGS:
        parts.append(heading)
        if heading == "# SOURCE CHECK":
            parts.append(
                f"Merged from {count} chunk ledgers produced by adaptive "
                "chunking (soft threshold — never a refusal cap). Record IDs "
                "are chunk-scoped."
            )
        for index, sections in enumerate(per_chunk, start=1):
            body = sections[heading]
            if body:
                parts.append(f"**[Chunk {index} of {count}]**")
                parts.append(body)
        if heading == "# CONFLICTS AND POSSIBLE SUPERSESSION" and duplicates:
            parts.append(
                f"- Merge note: {duplicates} statement(s) appear in multiple "
                "chunks (possible duplicates). Records preserved, not "
                "deleted; review during audit."
            )
        parts.append("")
    return "\n".join(parts).strip() + "\n"
