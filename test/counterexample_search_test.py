import pytest
from riemann.counterexample_search import best_witness
from riemann.counterexample_search import search
from riemann.counterexample_search import witness_value


def test_witness_value():
    assert abs(witness_value(10080) - 1.755814) < 1e-5


def test_search_failure():
    with pytest.raises(ValueError):
        search(6000)


def test_search_success():
    assert 5040 == search(10000, search_start = 5040)


def test_best_witness_million():
    assert 10080 == best_witness(1000000, search_start = 5041)
