from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
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


def hash_divisor_sums(sums: List[RiemannDivisorSum]) -> str:
    hash_input = ",".join(f"{rds.n},{rds.witness_value:5.4f}" for rds in sums) 
    return sha256(bytes(hash_input, "utf-8")).hexdigest()


class SearchBlockState(Enum):
    NOT_STARTED = 1
    IN_PROGRESS = 2
    FINISHED = 3
    FAILED = 4


@dataclass(frozen=True)
class SearchMetadata:
    start_time: datetime
    end_time: datetime
    search_state_type: str
    state: SearchBlockState
    starting_search_state: SearchState
    ending_search_state: SearchState

    '''
    The hexdigest of the SHA-256 hash of a string
    representation of the witness values of this search block.
    The field may be None if this value has not yet been
    computed.
    
    The format for the string before hashing is

    N_1,WITNESS_VALUE_1,N_2,WITNESS_VALUE_2,...

    where WITNESS_VALUE_i formatted with %5.4f is the approximate witness value
    for N_i.

    Example, for a block starting with 10080 and ending with 10082, the string
    before hashing is

    10080,1.7558,100081,0.4775,10082,0.6849
    
    And the hash is 

    d6062a3151b57f7a65401cbc41d94239ff150b374269d595d9280849d4e2123f
    '''
    block_hash: str = None
