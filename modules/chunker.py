def chunk_text(text: str, max_len: int = 2500):
    """
    Split transcript into manageable chunks by words.
    Useful for QA, Diarization, Summarization, etc.
    """
    words = text.split()
    chunks, current, length = [], [], 0

    for word in words:
        length += len(word) + 1
        if length > max_len:
            chunks.append(" ".join(current))
            current, length = [word], len(word) + 1
        else:
            current.append(word)

    if current:
        chunks.append(" ".join(current))

    return chunks
