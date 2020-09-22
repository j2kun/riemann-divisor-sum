from riemann.search_strategy import ExhaustiveSearchStrategy
from riemann.search_strategy import SuperabundantEnumerationIndex
from riemann.search_strategy import SuperabundantSearchStrategy
import pytest


@pytest.mark.parametrize(
    'make_strategy,expected_numbers_1,expected_numbers_2',
    [(ExhaustiveSearchStrategy, [5041, 5042, 5043, 5044], [5045, 5046, 5047, 5048]),
     (SuperabundantSearchStrategy, [2, 4, 6, 8], [12, 30, 16, 24]),
     ])
def test_search_strategy_uninitialized(make_strategy, expected_numbers_1, expected_numbers_2):
    search = make_strategy()
    searched_numbers = set([x.n for x in search.next_batch(4)])
    assert searched_numbers == set(expected_numbers_1)
    searched_numbers = set([x.n for x in search.next_batch(4)])
    assert searched_numbers == set(expected_numbers_2)


@pytest.mark.parametrize(
    'make_strategy,search_state,expected_numbers',
    [(ExhaustiveSearchStrategy, 100, [100, 101]),
     (SuperabundantSearchStrategy,
      SuperabundantEnumerationIndex(level=5, index_in_level=1),
      [16 * 3, 8 * 9]),
     ])
def test_search_strategy_initialized(make_strategy, search_state, expected_numbers):
    search = make_strategy().starting_from(search_state)
    searched_numbers = set([x.n for x in search.next_batch(2)])
    assert searched_numbers == set(expected_numbers)


@pytest.mark.parametrize(
    'make_strategy,search_state,expected_ending_state',
    [(ExhaustiveSearchStrategy, 100, 102),
     (SuperabundantSearchStrategy,
      SuperabundantEnumerationIndex(level=5, index_in_level=1),
      SuperabundantEnumerationIndex(level=5, index_in_level=3)),
     (SuperabundantSearchStrategy,
      SuperabundantEnumerationIndex(level=4, index_in_level=4),
      SuperabundantEnumerationIndex(level=5, index_in_level=1))
     ])
def test_search_strategy_state(make_strategy, search_state, expected_ending_state):
    search = make_strategy().starting_from(search_state)
    assert search.search_state() == search_state
    search.next_batch(2)
    assert search.search_state() == expected_ending_state


@pytest.mark.parametrize(
    'make_strategy,search_state',
    [(ExhaustiveSearchStrategy, 100),
     (SuperabundantSearchStrategy,
      SuperabundantEnumerationIndex(level=5, index_in_level=1))])
def test_search_state_reset(make_strategy, search_state):
    search = make_strategy().starting_from(search_state)
    batch = search.next_batch(2)
    batch_2 = search.starting_from(search_state).next_batch(2)
    assert batch == batch_2
