from whs_rag.chunking import chunk_elements, format_chunk


def el(type_, content, page=0):
    return {"type": type_, "content": content, "page": page}


def test_heading_starts_new_chunk_and_sets_section():
    chunks = chunk_elements(
        [
            el("section_header", "Trenches"),
            el("text", "Shore trenches 1.5 m or deeper.", page=25),
            el("section_header", "Lighting"),
            el("text", "Bricklaying needs 160 lux.", page=84),
        ]
    )
    assert [c["section"] for c in chunks] == ["Trenches", "Lighting"]
    assert "1.5 m" in chunks[0]["text"] and "160 lux" in chunks[1]["text"]


def test_splits_when_over_max_chars():
    chunks = chunk_elements([el("text", "a" * 60), el("text", "b" * 60)], max_chars=100)
    assert len(chunks) == 2


def test_long_element_is_never_split():
    table = "<table>" + "x" * 500 + "</table>"
    chunks = chunk_elements([el("table", table)], max_chars=100)
    assert len(chunks) == 1 and chunks[0]["text"] == table


def test_page_is_one_based_and_taken_from_first_element():
    chunks = chunk_elements([el("text", "first", page=9), el("text", "second", page=10)])
    assert chunks[0]["page"] == 10


def test_missing_page_and_empty_content_are_handled():
    chunks = chunk_elements(
        [
            el("text", "   "),
            el("text", None),
            {"type": "text", "content": "no page", "page": float("nan")},
        ]
    )
    assert chunks == [{"section": "", "page": None, "text": "no page"}]


def test_format_chunk_prefixes_source():
    assert format_chunk("a.pdf", "Intro", "body") == "[a.pdf | Intro]\nbody"
