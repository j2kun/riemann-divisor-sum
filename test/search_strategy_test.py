import pytest
from riemann.search_strategy import ExhaustiveSearchStrategy


def test_exhaustive_search_strategy_uninitialized():
    search = ExhaustiveSearchStrategy()
    searched_numbers = set([x.n for x in search.next_batch(2)])
    assert searched_numbers == set([5041, 5042])
    searched_numbers = set([x.n for x in search.next_batch(2)])
    assert searched_numbers == set([5043, 5044])


def test_exhaustive_search_strategy_initialized():
    search = ExhaustiveSearchStrategy().starting_from(100)
    searched_numbers = set([x.n for x in search.next_batch(2)])
    assert searched_numbers == set([100, 101])


def test_exhaustive_search_strategy_state():
    search = ExhaustiveSearchStrategy().starting_from(100)
    assert search.search_state() == 100
    searched_numbers = set([x.n for x in search.next_batch(2)])
    assert search.search_state() == 102


def test_search_state_reset():
    make_strategy = ExhaustiveSearchStrategy
    search_state = 100
    search = make_strategy().starting_from(search_state)
    batch = search.next_batch(2)
    batch_2 = search.starting_from(search_state).next_batch(2)
    assert batch == batch_2
