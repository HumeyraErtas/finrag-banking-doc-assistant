from __future__ import annotations
from dataclasses import dataclass
from typing import List
import re


@dataclass
class ChunkOut:
    chunk_index: int
    page_start: int
    page_end: int
    text: str


def clean_text(s: str) -> str:
    s = s.replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def chunk_pages(pages: list[tuple[int, str]], chunk_size: int = 900, overlap: int = 150) -> List[ChunkOut]:
    """
    pages: [(page_number, page_text), ...]
    Creates chunks by concatenating pages, splitting into approx. char-size windows with overlap.
    Stores page range for citations.

    Notes:
    - Char-based chunking is robust for PDFs with messy formatting.
    - If you want token-aware chunking later, you can swap this.
    """
    full = []
    page_map = []  # for each char segment, which page it belongs to
    for pno, txt in pages:
        txt = clean_text(txt)
        if not txt:
            continue
        start_char = sum(len(t) for t, _ in full)
        full.append((txt + "\n\n", pno))
        # we store page per appended segment, and infer range later
    merged = "".join(t for t, _ in full)

    # build char -> page number approximation by segments
    # for each segment, we know its char start/end, map range
    ranges = []
    cursor = 0
    for t, pno in full:
        ranges.append((cursor, cursor + len(t), pno))
        cursor += len(t)

    def page_for_char(idx: int) -> int:
        # linear scan ok for typical doc sizes; can be optimized
        for a, b, pno in ranges:
            if a <= idx < b:
                return pno
        return ranges[-1][2] if ranges else 1

    chunks: List[ChunkOut] = []
    if not merged.strip():
        return chunks

    i = 0
    cidx = 0
    n = len(merged)
    while i < n:
        j = min(i + chunk_size, n)
        text = merged[i:j].strip()
        if text:
            ps = page_for_char(i)
            pe = page_for_char(j - 1)
            chunks.append(ChunkOut(chunk_index=cidx, page_start=ps, page_end=pe, text=text))
            cidx += 1
        if j == n:
            break
        i = max(0, j - overlap)

    return chunks
