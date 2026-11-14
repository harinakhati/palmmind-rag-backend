import pytest

from app.services.chunking import (
    fixed_size_chunking,
    recursive_character_chunking,
)


# ==========================================
# Fixed-size chunking tests
# ==========================================

def test_fixed_chunking_with_empty_text():
    assert fixed_size_chunking("") == []


def test_fixed_chunking_with_short_text():
    text = "This is a short document."

    result = fixed_size_chunking(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert len(result) == 1
    assert result[0] == text


def test_fixed_chunking_with_long_text():
    text = "A" * 250

    result = fixed_size_chunking(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert len(result) > 1
    assert all(len(chunk) <= 100 for chunk in result)


def test_fixed_chunking_preserves_overlap():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 5

    result = fixed_size_chunking(
        text,
        chunk_size=50,
        overlap=10,
    )

    assert result[0][-10:] == result[1][:10]


# ==========================================
# Recursive character chunking tests
# ==========================================

def test_recursive_chunking_with_empty_text():
    assert recursive_character_chunking("") == []


def test_recursive_chunking_with_short_text():
    text = "This is a short document."

    result = recursive_character_chunking(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert len(result) == 1
    assert result[0] == text


def test_recursive_chunking_with_long_text():
    text = (
        "First paragraph contains some information.\n\n"
        "Second paragraph contains more information.\n\n"
        "Third paragraph contains additional information."
    )

    result = recursive_character_chunking(
        text,
        chunk_size=60,
        overlap=10,
    )

    assert len(result) > 1
    assert all(len(chunk) <= 60 for chunk in result)


def test_recursive_chunking_preserves_overlap():
    text = (
        "This is the first paragraph containing useful information. "
        "This is the second paragraph containing more useful information. "
        "This is the third paragraph containing additional information."
    )

    result = recursive_character_chunking(
        text,
        chunk_size=60,
        overlap=15,
    )

    assert len(result) > 1

    for previous, current in zip(result, result[1:]):
        assert previous[-15:] in current


def test_recursive_chunks_do_not_exceed_chunk_size():
    text = "This is a long document. " * 30

    result = recursive_character_chunking(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert all(len(chunk) <= 100 for chunk in result)


def test_recursive_chunking_preserves_all_text():
    text = (
        "Paragraph one contains information.\n\n"
        "Paragraph two contains more information."
    )

    result = recursive_character_chunking(
        text,
        chunk_size=40,
        overlap=10,
    )

    reconstructed = result[0]

    for chunk in result[1:]:
        reconstructed += chunk[10:]

    assert reconstructed == text


# ==========================================
# Invalid chunking settings
# ==========================================

@pytest.mark.parametrize(
    "chunk_size, overlap",
    [
        (0, 0),
        (-10, 0),
        (100, -1),
        (100, 100),
        (100, 150),
    ],
)
def test_invalid_chunk_settings(chunk_size, overlap):

    with pytest.raises(ValueError):
        fixed_size_chunking(
            "Sample text",
            chunk_size=chunk_size,
            overlap=overlap,
        )

    with pytest.raises(ValueError):
        recursive_character_chunking(
            "Sample text",
            chunk_size=chunk_size,
            overlap=overlap,
        )
        
def test_recursive_chunking_prefers_paragraph_boundaries():
    text = (
        "A" * 40
        + "\n\n"
        + "B" * 40
    )

    result = recursive_character_chunking(
        text,
        chunk_size=60,
        overlap=10,
    )

    assert len(result) > 1
    assert result[0].endswith("\n\n")