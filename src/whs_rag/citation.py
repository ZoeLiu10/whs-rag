import re

# Matches citations like [first_aid_in_the_work.pdf#p17]
CITATION_RE = re.compile(r"\[[^\]]+\.pdf#p\d+\]")


def has_citation(text):
    return bool(CITATION_RE.search(text or ""))


def source_label(file_name, page):
    """Build the label shown to the model, e.g. first_aid_in_the_work.pdf#p14.
    AI Search returns numeric columns as floats (14.0), so cast to int."""
    if page is None:
        return f"{file_name}#p?"
    return f"{file_name}#p{int(page)}"


def normalize_citations(text):
    """Some models cite with full-width brackets 【...】; convert them to [...]."""
    return (text or "").replace("【", "[").replace("】", "]")
