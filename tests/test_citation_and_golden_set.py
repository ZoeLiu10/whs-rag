import pytest

from whs_rag.citation import has_citation
from whs_rag.golden_set import CONSTRUCTION, FIRST_AID, RISK, in_scope, out_of_scope


@pytest.mark.parametrize("text,expected", [
    ("Shore it [construction_work.pdf#p26].", True),
    ("See [first_aid_in_the_work.pdf#p17] and [x.pdf#p3]", True),
    ("Shore it (construction_work.pdf page 26).", False),
    ("", False),
    (None, False),
])
def test_has_citation(text, expected):
    assert has_citation(text) is expected


# Data tests: a broken golden set silently breaks every score, so CI checks its shape.
def test_in_scope_items_are_complete():
    sources = {CONSTRUCTION, FIRST_AID, RISK}
    for item in in_scope:
        assert set(item["inputs"]) == {"question"}, "rag_app takes exactly one argument: question"
        exp = item["expectations"]
        assert exp["expected_facts"], item["inputs"]["question"]
        assert exp["expected_source"] in sources, item["inputs"]["question"]


def test_out_of_scope_items_have_no_expectations():
    for item in out_of_scope:
        assert set(item) == {"inputs"} and set(item["inputs"]) == {"question"}


def test_no_duplicate_questions():
    questions = [i["inputs"]["question"] for i in in_scope + out_of_scope]
    assert len(questions) == len(set(questions))
