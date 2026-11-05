"""Section-aware chunking.

Pure Python on purpose: no Spark, no Databricks imports, so it can be unit-tested in CI.
"""

import math

HEADING_TYPES = {"title", "section_header"}


def _page_number(raw):
    """ai_parse_document page_id is 0-based; return a 1-based page, or None if missing/NaN."""
    if raw is None:
        return None
    if isinstance(raw, float) and math.isnan(raw):
        return None
    return int(raw) + 1


def chunk_elements(elements, max_chars=2000):
    """Group parsed elements of ONE document into chunks.

    elements: dicts in document order, with keys "type", "content" and "page" (0-based page_id).
    Rules:
      - a title / section_header closes the current chunk and becomes the section label
      - a chunk is closed before it would grow past max_chars
      - an element is never split, so a table longer than max_chars stays one chunk
    Returns dicts with keys "section", "page" (1-based page where the chunk starts) and "text".
    """
    chunks = []
    buf, size, page, section = [], 0, None, ""

    def flush():
        nonlocal buf, size, page
        if buf:
            chunks.append({"section": section, "page": page, "text": "\n\n".join(buf)})
        buf, size, page = [], 0, None

    for el in elements:
        text = (el.get("content") or "").strip()
        if not text:
            continue
        if el.get("type") in HEADING_TYPES:
            flush()
            section = text
            continue
        if buf and size + len(text) > max_chars:
            flush()
        if page is None:
            page = _page_number(el.get("page"))
        buf.append(text)
        size += len(text)
    flush()
    return chunks


def format_chunk(file_name, section, text):
    """Prefix each chunk with its source so it still makes sense when read on its own."""
    return f"[{file_name} | {section}]\n{text}"
