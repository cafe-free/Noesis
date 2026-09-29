import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TextChunk:
    chunk_index: int
    content: str
    start_char: int
    end_char: int
    token_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


def split_into_semantic_segments(text: str) -> list[str]:
    """
    Splits text by natural semantic boundaries: paragraphs, newlines, and sentence endings.
    """
    # First split by paragraphs
    paragraphs = text.split("\n\n")
    segments: list[str] = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If paragraph is reasonable size, keep it
        if len(para) <= 600:
            segments.append(para)
        else:
            # Split paragraph into sentences
            # Regex splits on sentence-ending punctuation followed by space
            sentence_splits = re.split(r"(?<=[.!?])\s+", para)
            for s in sentence_splits:
                s = s.strip()
                if not s:
                    continue
                if len(s) <= 600:
                    segments.append(s)
                else:
                    # Split very long sentences by words
                    words = s.split(" ")
                    current_buf: list[str] = []
                    curr_len = 0
                    for w in words:
                        if curr_len + len(w) + 1 > 400:
                            segments.append(" ".join(current_buf))
                            current_buf = [w]
                            curr_len = len(w)
                        else:
                            current_buf.append(w)
                            curr_len += len(w) + 1
                    if current_buf:
                        segments.append(" ".join(current_buf))

    return segments


def chunk_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[TextChunk]:
    """
    Chunks text with sliding window overlap respecting semantic boundaries.
    """
    clean_text = text.strip()
    if not clean_text:
        return []

    # If entire text fits in one chunk, return it directly
    if len(clean_text) <= chunk_size:
        return [
            TextChunk(
                chunk_index=0,
                content=clean_text,
                start_char=0,
                end_char=len(clean_text),
                token_count=len(clean_text.split()),
                metadata={"char_length": len(clean_text)},
            )
        ]

    segments = split_into_semantic_segments(clean_text)
    if not segments:
        return []

    chunks: list[TextChunk] = []
    current_segments: list[str] = []
    current_length = 0
    seg_idx = 0
    chunk_index = 0

    while seg_idx < len(segments):
        seg = segments[seg_idx]
        seg_len = len(seg)

        # If adding this segment exceeds chunk_size and we already have some segments:
        if current_segments and (current_length + seg_len + 2 > chunk_size):
            chunk_content = "\n\n".join(current_segments).strip()
            # Calculate char offsets in original text
            start_pos = clean_text.find(chunk_content[:50]) if len(chunk_content) >= 50 else clean_text.find(chunk_content)
            if start_pos == -1:
                start_pos = 0
            end_pos = start_pos + len(chunk_content)

            chunks.append(
                TextChunk(
                    chunk_index=chunk_index,
                    content=chunk_content,
                    start_char=start_pos,
                    end_char=end_pos,
                    token_count=len(chunk_content.split()),
                    metadata={"char_length": len(chunk_content)},
                )
            )
            chunk_index += 1

            # Backtrack segments for overlap
            overlap_length = 0
            backtrack_count = 0
            for prev_seg in reversed(current_segments):
                if overlap_length + len(prev_seg) <= chunk_overlap:
                    overlap_length += len(prev_seg) + 2
                    backtrack_count += 1
                else:
                    break

            if backtrack_count > 0:
                current_segments = current_segments[-backtrack_count:]
                current_length = sum(len(s) for s in current_segments) + (len(current_segments) - 1) * 2
            else:
                current_segments = []
                current_length = 0

        current_segments.append(seg)
        current_length += seg_len + (2 if len(current_segments) > 1 else 0)
        seg_idx += 1

    # Final remaining chunk
    if current_segments:
        chunk_content = "\n\n".join(current_segments).strip()
        start_pos = clean_text.find(chunk_content[:50]) if len(chunk_content) >= 50 else clean_text.find(chunk_content)
        if start_pos == -1:
            start_pos = 0
        end_pos = start_pos + len(chunk_content)

        chunks.append(
            TextChunk(
                chunk_index=chunk_index,
                content=chunk_content,
                start_char=start_pos,
                end_char=end_pos,
                token_count=len(chunk_content.split()),
                metadata={"char_length": len(chunk_content)},
            )
        )

    return chunks
