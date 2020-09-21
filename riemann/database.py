'''An interface for a database containing divisor sums.'''

from abc import ABC
from abc import abstractmethod
from riemann.types import RiemannDivisorSum
from riemann.types import SummaryStats
from typing import List


class DivisorDb(ABC):
    @abstractmethod
    def load() -> List[RiemannDivisorSum]:
        '''Load the entire database.'''
        pass

    @abstractmethod
    def upsert(data: List[RiemannDivisorSum]) -> None:
        '''Insert or update the given list of data points.'''
        pass

    @abstractmethod
    def summarize() -> SummaryStats:
        '''Summarize the contents of the database.'''
        pass
