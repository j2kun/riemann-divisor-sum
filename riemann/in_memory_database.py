'''A simple in-memory divisor database.'''
from typing import List

from riemann.database import DivisorDb
from riemann.database import SearchMetadataDb
from riemann.types import RiemannDivisorSum
from riemann.types import SearchMetadata
from riemann.types import SummaryStats


class InMemoryDivisorDb(DivisorDb, SearchMetadataDb):
    def __init__(self):
        self.data = dict()
        self.metadata = list()

    def load(self) -> List[RiemannDivisorSum]:
        return list(self.data.values())

    def upsert(self, records: List[RiemannDivisorSum]) -> None:
        for record in records:
            self.data[record.n] = record

    def summarize(self) -> SummaryStats:
        if not self.data:
            return SummaryStats(largest_computed_n=None,
                                largest_witness_value=None)

        largest_computed_n = max(self.data.values(), key=lambda x: x.n)
        largest_witness_value = max(self.data.values(),
                                    key=lambda x: x.witness_value)

        return SummaryStats(largest_computed_n=largest_computed_n,
                            largest_witness_value=largest_witness_value)

    def latest_search_metadata(self, search_state_type) -> SearchMetadata:
        if not self.metadata:
            return None
        return max(self.metadata, key=lambda m: m.end_time)

    def insert_search_metadata(self, metadata) -> None:
        self.metadata.append(metadata)
