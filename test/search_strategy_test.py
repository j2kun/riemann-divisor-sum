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
    blocks = search.generate_search_blocks(count=2, batch_size=4)
    searched_numbers = set([x.n for x in search.process_block(blocks[0])])
    assert searched_numbers == set(expected_numbers_1)
    searched_numbers = set([x.n for x in search.process_block(blocks[1])])
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
    blocks = search.generate_search_blocks(count=1, batch_size=2)
    searched_numbers = set([x.n for x in search.process_block(blocks[0])])
    assert searched_numbers == set(expected_numbers)


@pytest.mark.parametrize(
    'make_strategy,search_index',
    [(ExhaustiveSearchStrategy, ExhaustiveSearchIndex(n=100)),
     (SuperabundantSearchStrategy,
      SuperabundantEnumerationIndex(level=5, index_in_level=1))])
def test_search_index_reset(make_strategy, search_index):
    search = make_strategy().starting_from(search_index)
    blocks = search.generate_search_blocks(count=2, batch_size=2)
    blocks_2 = search.starting_from(
        search_index).generate_search_blocks(count=2, batch_size=2)

    assert blocks[0].starting_search_index == blocks_2[0].starting_search_index
    assert blocks[1].starting_search_index == blocks_2[1].starting_search_index


def test_superabundant_exactly_landing_on_level_boundary():
    search = SuperabundantSearchStrategy().starting_from(
        SuperabundantEnumerationIndex(level=4, index_in_level=1))
    '''
    The parititions of 4 are 

    [[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]]

    So if the index in the level is 1, a batch size of 4 should land
    exactly on the boundary of the level.
    '''
    blocks = search.generate_search_blocks(count=2, batch_size=4)
    assert blocks[0].starting_search_index == SuperabundantEnumerationIndex(
        level=4, index_in_level=1)
    assert blocks[0].ending_search_index == SuperabundantEnumerationIndex(
        level=4, index_in_level=4)
    assert blocks[1].starting_search_index == SuperabundantEnumerationIndex(
        level=5, index_in_level=0)
    assert blocks[1].ending_search_index == SuperabundantEnumerationIndex(
        level=5, index_in_level=3)
