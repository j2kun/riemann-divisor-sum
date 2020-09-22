'''An interface describing search strategies.'''
# this import ensures we can have X as a return type for a method for class X
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from riemann.divisor import compute_riemann_divisor_sums
from typing import List
from typing import TypeVar

SearchState = TypeVar('SearchState')


class SearchStrategy(ABC):
    @abstractmethod
    def starting_from(self, search_state: SearchState) -> SearchStrategy:
        '''Reset the search strategy to search from a given state.'''
        pass

    @abstractmethod
    def search_state(self) -> SearchState:
        '''Get an object describing the current state of the enumeration.'''
        pass

    @abstractmethod
    def next_batch(self, batch_size: int) -> List[RiemannDivisorSum]:
        '''Process the next batch of Riemann Divisor Sums'''
        pass


class ExhaustiveSearchStrategy(SearchStrategy):
    '''A search strategy that tries every positive integer starting from 5041.'''
    def __init__(self):
        self.search_index = 5041

    def starting_from(self, search_state: int) -> ExhaustiveSearchStrategy:
        self.search_index = search_state
        return self

    def search_state(self) -> int:
        return self.search_index

    def next_batch(self, batch_size: int) -> List[RiemannDivisorSum]:
        ending_n = self.search_index + batch_size - 1
        sums = compute_riemann_divisor_sums(self.search_index, ending_n)
        self.search_index = ending_n + 1
        return sums
