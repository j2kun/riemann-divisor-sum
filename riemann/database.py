'''An interface for a database containing divisor sums.'''

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RiemannDivisorSum:
    n: int
    divisor_sum: int
    witness_value: float


@dataclass(frozen=True)
class SummaryStats:
    largest_computed_n: RiemannDivisorSum
    largest_witness_value: RiemannDivisorSum


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
