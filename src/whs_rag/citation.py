import re

# Matches citations like [first_aid_in_the_work.pdf#p17]
CITATION_RE = re.compile(r"\[[^\]]+\.pdf#p\d+\]")


def has_citation(text):
    return bool(CITATION_RE.search(text or ""))
