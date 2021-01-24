'''An interface for a database containing divisor sums.'''
from abc import ABC
from abc import abstractmethod
from typing import List

from riemann.types import RiemannDivisorSum
from riemann.types import SearchMetadata
from riemann.types import SummaryStats


class DivisorDb(ABC):
    @abstractmethod
    def initialize_schema(self):
        '''Create the schema for a database, idempotently.'''
        pass

    @abstractmethod
    def load(self) -> List[RiemannDivisorSum]:
        '''Load the entire database.'''
        pass

    @abstractmethod
    def summarize(self) -> SummaryStats:
        '''Summarize the contents of the database.'''
        pass

    @abstractmethod
    def insert_search_blocks(self, blocks: List[SearchMetadata]) -> None:
        '''Insert new search blocks, and mark them as not started.'''
        pass

    @abstractmethod
    def claim_next_search_block(self, search_state_type: str) -> SearchMetadata:
        '''Claim the next search block, and mark it as started.'''
        pass

    @abstractmethod
    def finish_search_block(self,
                            metadata: SearchMetadata,
                            divisor_sums: List[RiemannDivisorSum]) -> None:
        '''
        Mark a search block as finished, and insert the corresponding divisor
        sums.
        '''
        pass
