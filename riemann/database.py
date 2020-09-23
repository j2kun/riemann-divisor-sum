'''An interface for a database containing divisor sums.'''

from abc import ABC
from abc import abstractmethod
from riemann.types import RiemannDivisorSum
from riemann.types import SearchMetadata
from riemann.types import SummaryStats
from typing import List


class DivisorDb(ABC):
    @abstractmethod
    def load(self) -> List[RiemannDivisorSum]:
        '''Load the entire database.'''
        pass

    @abstractmethod
    def upsert(self, data: List[RiemannDivisorSum]) -> None:
        '''Insert or update the given list of data points.'''
        pass

    @abstractmethod
    def summarize(self) -> SummaryStats:
        '''Summarize the contents of the database.'''
        pass


class SearchMetadataDb(ABC):
    @abstractmethod
    def latest_search_metadata(self, search_state_type: str) -> SearchMetadata:
        pass

    @abstractmethod
    def insert_search_metadata(self, metadata: SearchMetadata) -> None:
        pass
