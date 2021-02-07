'''An interface describing search strategies.'''
# this import ensures we can have X as a return type for a method for class X
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from copy import deepcopy
from typing import Iterator
from typing import List

from riemann import divisor
from riemann import superabundant
from riemann.superabundant import CachedPartitionsOfN
from riemann.superabundant import partition_to_prime_factorization
from riemann.types import ExhaustiveSearchIndex
from riemann.types import RiemannDivisorSum
from riemann.types import SearchIndex
from riemann.types import SearchMetadata
from riemann.types import SuperabundantEnumerationIndex


class SearchStrategy(ABC):
    @abstractmethod
    def index_name(self) -> str:
        '''The name of the SearchIndex subclass used with this strategy.'''
        pass

    @abstractmethod
    def starting_from(self, search_index: SearchIndex) -> SearchStrategy:
        '''Reset the search strategy to search from a given state.'''
        pass

    @abstractmethod
    def generate_search_blocks(self, count: int, batch_size: int) -> List[SearchMetadata]:
        '''Generate new search blocks to process.'''
        pass

    @abstractmethod
    def process_block(self, block: SearchMetadata) -> List[RiemannDivisorSum]:
        '''Compute the Riemann divisor sums for the given block.'''
        pass


def search_strategy_by_name(strategy_name):
    lookup = {
        cls.__name__: cls
        for cls in [ExhaustiveSearchStrategy, SuperabundantSearchStrategy]
    }
    if strategy_name not in lookup:
        raise ValueError(f"Unknown strategy name {strategy_name}, "
                         f"should be one of {list(lookup.keys())}")

    return lookup[strategy_name]


class ExhaustiveSearchStrategy(SearchStrategy):
    '''A search strategy that tries every positive integer starting from 5041.'''

    def __init__(self):
        self._search_index = ExhaustiveSearchIndex(n=5041)
        self._index_name = self._search_index.__class__.__name__

    def starting_from(
            self,
            search_index: ExhaustiveSearchIndex) -> ExhaustiveSearchStrategy:
        self._search_index = search_index
        return self

    def generate_search_blocks(self, count: int, batch_size: int) -> List[SearchMetadata]:
        start = self._search_index.n
        blocks = []
        for i in range(count):
            starting_index = ExhaustiveSearchIndex(n=start)
            ending_index = ExhaustiveSearchIndex(n=start+batch_size-1)
            start += batch_size
            blocks.append(SearchMetadata(
                starting_search_index=starting_index,
                ending_search_index=ending_index,
                search_index_type=self.index_name(),
            ))
        return blocks

    def process_block(self, block: SearchMetadata) -> List[RiemannDivisorSum]:
        return divisor.compute_riemann_divisor_sums(block.starting_search_index.n, block.ending_search_index.n)

    def index_name(self) -> str:
        return self._index_name


class SuperabundantSearchStrategy(SearchStrategy):
    '''A search strategy that iterates over possibly superabundant numbers.'''

    def __init__(self):
        self._search_index = SuperabundantEnumerationIndex(
            level=1, index_in_level=0)
        self.current_level = [[1]]
        self.__maybe_reset_current_level__()
        self._index_name = self._search_index.__class__.__name__

    def index_name(self) -> str:
        return self._index_name

    def starting_from(
        self, search_index: SuperabundantEnumerationIndex
    ) -> SuperabundantSearchStrategy:
        self._search_index = search_index
        self.__maybe_reset_current_level__()
        return self

    def generate_search_blocks(self, count: int, batch_size: int) -> List[SearchMetadata]:
        return [self.generate_next_block(batch_size) for i in range(count)]

    def generate_next_block(self, batch_size: int) -> SearchMetadata:
        starting_index = deepcopy(self._search_index)

        '''
        Because a block can cross multiple levels, we need to possibly split
        the block into pieces.
        '''
        ending_level_index = self._search_index.index_in_level + batch_size - 1
        while ending_level_index >= len(self.current_level):
            ending_level_index -= len(self.current_level)
            self._search_index = SuperabundantEnumerationIndex(
                level=self._search_index.level+1, index_in_level=0)
            self.__maybe_reset_current_level__()  # definitely

        ending_index = SuperabundantEnumerationIndex(
            level=self._search_index.level,
            index_in_level=ending_level_index)

        if (ending_level_index == len(self.current_level) - 1):
            self._search_index = SuperabundantEnumerationIndex(
                level=self._search_index.level+1,
                index_in_level=0)
            self.__maybe_reset_current_level__()  # definitely
        else:
            self._search_index = SuperabundantEnumerationIndex(
                level=self._search_index.level,
                index_in_level=ending_level_index+1)

        return SearchMetadata(
            starting_search_index=starting_index,
            ending_search_index=ending_index,
            search_index_type='SuperabundantEnumerationIndex',
        )

    def process_block(self, block: SearchMetadata) -> List[RiemannDivisorSum]:
        sums = []
        current_index = block.starting_search_index
        ending_index = block.ending_search_index
        current_level = CachedPartitionsOfN(current_index.level)

        while current_index.level < ending_index.level:
            for i in range(current_index.index_in_level, len(current_level)):
                fac = partition_to_prime_factorization(current_level[i])
                sums.append(superabundant.compute_riemann_divisor_sum(fac))

            current_index = SuperabundantEnumerationIndex(
                level=current_index.level+1,
                index_in_level=0,
            )
            current_level = CachedPartitionsOfN(current_index.level)

        for i in range(current_index.index_in_level,
                       ending_index.index_in_level+1):
            fac = partition_to_prime_factorization(current_level[i])
            sums.append(superabundant.compute_riemann_divisor_sum(fac))

        return sums

    def __maybe_reset_current_level__(self):
        '''Idempotently compute the next level of the enumeration.'''
        if self.current_level[0] != self._search_index.level:
            self.current_level = CachedPartitionsOfN(
                n=self._search_index.level)
