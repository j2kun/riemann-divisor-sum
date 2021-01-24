'''An interface describing search strategies.'''
# this import ensures we can have X as a return type for a method for class X
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import List

from riemann import divisor
from riemann import superabundant
from riemann.superabundant import CachedPartitionsOfN
from riemann.superabundant import partition_to_prime_factorization
from riemann.types import ExhaustiveSearchIndex
from riemann.types import RiemannDivisorSum
from riemann.types import SearchIndex
from riemann.types import SuperabundantEnumerationIndex


class SearchStrategy(ABC):
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
        self._search_index = 5041

    def starting_from(
            self,
            search_index: ExhaustiveSearchIndex) -> ExhaustiveSearchStrategy:
        self._search_index = search_index.n
        return self

    def search_index(self) -> ExhaustiveSearchIndex:
        return ExhaustiveSearchIndex(n=self._search_index)

    def next_batch(self, batch_size: int) -> List[RiemannDivisorSum]:
        ending_n = self._search_index + batch_size - 1
        sums = divisor.compute_riemann_divisor_sums(self._search_index,
                                                    ending_n)
        self._search_index = ending_n + 1
        return sums


class SuperabundantSearchStrategy(SearchStrategy):
    '''A search strategy that iterates over possibly superabundant numbers.'''

    def __init__(self):
        self._search_index = SuperabundantEnumerationIndex(level=1,
                                                          index_in_level=0)
        self.current_level = [[1]]
        self.__maybe_reset_current_level__()

    def starting_from(
        self, search_index: SuperabundantEnumerationIndex
    ) -> SuperabundantSearchStrategy:
        self._search_index = search_index
        self.__maybe_reset_current_level__()
        return self

    def search_index(self) -> SuperabundantEnumerationIndex:
        return self._search_index

    def next_batch(self, batch_size: int) -> List[RiemannDivisorSum]:
        sums = []
        '''
        Because a batch can cross multiple levels, we need to possibly split
        the batch into pieces.
        '''
        ending_level_index = self._search_index.index_in_level + batch_size - 1
        while ending_level_index >= len(self.current_level):
            for i in range(self._search_index.index_in_level,
                           len(self.current_level)):
                fac = partition_to_prime_factorization(self.current_level[i])
                sums.append(superabundant.compute_riemann_divisor_sum(fac))

            ending_level_index -= len(self.current_level)
            self._search_index = SuperabundantEnumerationIndex(
                level=self._search_index.level + 1, index_in_level=0)
            self.__maybe_reset_current_level__()  # definitely

        for i in range(self._search_index.index_in_level,
                       ending_level_index + 1):
            fac = partition_to_prime_factorization(self.current_level[i])
            sums.append(superabundant.compute_riemann_divisor_sum(fac))
            self._search_index = SuperabundantEnumerationIndex(
                level=self._search_index.level,
                index_in_level=self._search_index.index_in_level + 1)

        return sums

    def __maybe_reset_current_level__(self):
        '''Idempotently compute the next level of the enumeration.'''
        if self.current_level[0] != self._search_index.level:
            self.current_level = CachedPartitionsOfN(n=self._search_index.level)
