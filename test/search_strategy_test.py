import pytest
from riemann.search_strategy import ExhaustiveSearchIndex
from riemann.search_strategy import ExhaustiveSearchStrategy
from riemann.search_strategy import SuperabundantEnumerationIndex
from riemann.search_strategy import SuperabundantSearchStrategy


@pytest.mark.parametrize(
    'make_strategy,expected_numbers_1,expected_numbers_2', [
        (ExhaustiveSearchStrategy, [5041, 5042, 5043, 5044
                                    ], [5045, 5046, 5047, 5048]),
        (SuperabundantSearchStrategy, [2, 4, 6, 8], [12, 30, 16, 24]),
    ])
def test_search_strategy_uninitialized(make_strategy, expected_numbers_1,
                                       expected_numbers_2):
    search = make_strategy()
    searched_numbers = set([x.n for x in search.next_batch(4)])
    assert searched_numbers == set(expected_numbers_1)
    searched_numbers = set([x.n for x in search.next_batch(4)])
    assert searched_numbers == set(expected_numbers_2)


@pytest.mark.parametrize('make_strategy,search_index,expected_numbers', [
    (ExhaustiveSearchStrategy, ExhaustiveSearchIndex(n=100), [100, 101]),
    (SuperabundantSearchStrategy,
     SuperabundantEnumerationIndex(level=5, index_in_level=1), [16 * 3, 8 * 9
                                                                ]),
])
def test_search_strategy_initialized(make_strategy, search_index,
                                     expected_numbers):
    search = make_strategy().starting_from(search_index)
    searched_numbers = set([x.n for x in search.next_batch(2)])
    assert searched_numbers == set(expected_numbers)


@pytest.mark.parametrize(
    'make_strategy,search_index,expected_ending_index',
    [(ExhaustiveSearchStrategy, ExhaustiveSearchIndex(n=100),
      ExhaustiveSearchIndex(n=102)),
     (SuperabundantSearchStrategy,
      SuperabundantEnumerationIndex(level=5, index_in_level=1),
      SuperabundantEnumerationIndex(level=5, index_in_level=3)),
     (SuperabundantSearchStrategy,
      SuperabundantEnumerationIndex(level=4, index_in_level=4),
      SuperabundantEnumerationIndex(level=5, index_in_level=1))])
def test_search_strategy_index(make_strategy, search_index,
                               expected_ending_index):
    search = make_strategy().starting_from(search_index)
    assert search.search_index() == search_index
    search.next_batch(2)
    assert search.search_index() == expected_ending_index


@pytest.mark.parametrize(
    'make_strategy,search_index',
    [(ExhaustiveSearchStrategy, ExhaustiveSearchIndex(n=100)),
     (SuperabundantSearchStrategy,
      SuperabundantEnumerationIndex(level=5, index_in_level=1))])
def test_search_index_reset(make_strategy, search_index):
    search = make_strategy().starting_from(search_index)
    batch = search.next_batch(2)
    batch_2 = search.starting_from(search_index).next_batch(2)
    assert batch == batch_2
