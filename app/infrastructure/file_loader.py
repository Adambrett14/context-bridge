"""Load .txt/.md uploads as text. UTF-8 preferred, graceful fallbacks, no size cap."""

from pathlib import PurePosixPath

from app.domain.errors import FileDecodeError, UnsupportedFileTypeError

SUPPORTED_EXTENSIONS = {".txt", ".md"}

_DECODE_ERROR_MESSAGE = (
    "The file could not be decoded as text. "
    "Use .txt/.md with UTF-8 text or paste the content."
)

# utf-8-sig FIRST: it strips a leading BOM when present and decodes plain
# UTF-8 identically when absent. Plain utf-8 would "succeed" on BOM bytes
# and leak an invisible \ufeff into the source text.
_ENCODINGS = ("utf-8-sig", "utf-8", "latin-1")


def load_text_upload(filename: str, raw: bytes) -> str:
    """Decode an uploaded file. Raises typed errors; never truncates content."""
    suffix = PurePosixPath(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{suffix or '(none)'}'. "
            "Use .txt or .md, or paste the content instead."
        )
    text: str | None = None
    for encoding in _ENCODINGS:
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None or "\x00" in text:
        raise FileDecodeError(_DECODE_ERROR_MESSAGE)
    return text
