from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List
from typing import Tuple

PrimeFactorization = List[Tuple[int, int]]
Partition = List[int]


@dataclass(frozen=True)
class RiemannDivisorSum:
    n: int
    divisor_sum: int
    witness_value: float

    def approx_equal(self, other, epsilon=1e-05) -> bool:
        return (isinstance(other, RiemannDivisorSum) and self.n == other.n
                and self.divisor_sum == other.divisor_sum
                and abs(self.witness_value - other.witness_value) < epsilon)


@dataclass(frozen=True)
class SummaryStats:
    largest_computed_n: RiemannDivisorSum
    largest_witness_value: RiemannDivisorSum


class SearchState(ABC):
    @abstractmethod
    def serialize(self) -> str:
        pass


@dataclass(frozen=True)
class ExhaustiveSearchIndex(SearchState):
    n: int

    def serialize(self) -> str:
        return str(self.n)


@dataclass(frozen=True)
class SuperabundantEnumerationIndex(SearchState):
    level: int
    index_in_level: int

    def serialize(self) -> str:
        return f"{self.level},{self.index_in_level}"


def deserialize_search_state(search_state_type: str,
                             serialized: str) -> SearchState:
    if search_state_type == ExhaustiveSearchIndex.__name__:
        return ExhaustiveSearchIndex(n=int(serialized))
    elif search_state_type == SuperabundantEnumerationIndex.__name__:
        level, index_in_level = serialized.split(",")
        return SuperabundantEnumerationIndex(
            level=int(level), index_in_level=int(index_in_level))
    else:
        raise ValueError(f"Unknown search_state_type {search_state_type}")


@dataclass(frozen=True)
class SearchMetadata:
    start_time: datetime
    end_time: datetime
    search_state_type: str
    starting_search_state: SearchState
    ending_search_state: SearchState
