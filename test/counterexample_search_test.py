import pytest
from riemann.counterexample_search import best_witness
from riemann.counterexample_search import search


def test_search_failure():
    with pytest.raises(ValueError):
        search(6000)


def test_search_success():
    assert 5040 == search(10000, search_start=5040)


def test_best_witness_million():
    assert 10080 == best_witness(1000000, search_start=5041)
