def _validate_chunk_settings(chunk_size: int, overlap: int) -> None:
    """Validate chunk size and overlap settings."""

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )


def fixed_size_chunking(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """Divide text into fixed-size chunks with overlap."""

    _validate_chunk_settings(chunk_size, overlap)

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = min(start + chunk_size, len(text))

        chunks.append(text[start:end])

        if end == len(text):
            break

        start += step

    return chunks


def _recursive_split_boundaries(
    text: str,
    chunk_size: int,
    separators: list[str],
    offset: int = 0,
    separator_priority: int = 0,
) -> list[tuple[int, int]]:
    """
    Recursively find preferred split boundaries.

    Lower priority number means a more preferred separator.
    """

    if len(text) <= chunk_size or not separators:
        return []

    separator = separators[0]
    remaining_separators = separators[1:]

    # Character-level fallback.
    if separator == "":
        return []

    # Try the next separator if this one does not exist.
    if separator not in text:
        return _recursive_split_boundaries(
            text,
            chunk_size,
            remaining_separators,
            offset,
            separator_priority + 1,
        )

    parts = text.split(separator)

    pieces = [
        part + separator
        for part in parts[:-1]
    ]

    pieces.append(parts[-1])

    boundaries = []
    current_position = offset

    for index, piece in enumerate(pieces):

        piece_start = current_position

        current_position += len(piece)

        # Recursively split oversized pieces.
        if len(piece) > chunk_size:
            boundaries.extend(
                _recursive_split_boundaries(
                    piece,
                    chunk_size,
                    remaining_separators,
                    piece_start,
                    separator_priority + 1,
                )
            )

        if index < len(pieces) - 1:
            boundaries.append(
                (current_position, separator_priority)
            )

    return boundaries

def recursive_character_chunking(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """
    Split text recursively using a separator hierarchy.

    Separator priority:
    1. Paragraph breaks
    2. Line breaks
    3. Spaces
    4. Character-level fallback

    Consecutive chunks preserve character-based overlap.
    """

    _validate_chunk_settings(chunk_size, overlap)

    text = text.strip()

    if not text:
        return []

    separators = ["\n\n", "\n", " ", ""]

    boundaries = _recursive_split_boundaries(
        text=text,
        chunk_size=chunk_size,
        separators=separators,
    )

    chunks = []
    start = 0

    while start < len(text):

        max_end = min(start + chunk_size, len(text))

        if max_end == len(text):
            chunks.append(text[start:max_end])
            break

        min_end = start + overlap + 1

        # Find boundaries that fit within the current chunk.
        candidates = [
            (position, priority)
            for position, priority in boundaries
            if min_end <= position <= max_end
        ]

        if candidates:
            # Prefer the highest-priority separator.
            best_priority = min(
                priority for _, priority in candidates
            )

            # Among boundaries with that priority,
            # select the one closest to the size limit.
            end = max(
                position
                for position, priority in candidates
                if priority == best_priority
            )

        else:
            # No suitable separator: split by character count.
            end = max_end

        chunks.append(text[start:end])

        # Preserve the configured character overlap.
        start = end - overlap

    return chunks