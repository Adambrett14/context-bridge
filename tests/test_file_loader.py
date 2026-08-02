"""File loader: extensions, decoding, binary rejection."""

import pytest

from app.domain.errors import FileDecodeError, UnsupportedFileTypeError
from app.infrastructure.file_loader import load_text_upload


def test_loads_markdown_bytes() -> None:
    assert load_text_upload("notes.md", b"# Hello") == "# Hello"


def test_loads_txt_bytes() -> None:
    assert load_text_upload("notes.txt", b"plain text") == "plain text"


def test_accepts_utf8_bom() -> None:
    assert load_text_upload("bom.txt", b"\xef\xbb\xbfhi") == "hi"


def test_rejects_unsupported_extension() -> None:
    with pytest.raises(UnsupportedFileTypeError):
        load_text_upload("report.pdf", b"%PDF-1.4")


def test_rejects_binary_content() -> None:
    with pytest.raises(FileDecodeError):
        load_text_upload("weird.txt", b"\x00\x01\x02binary")
