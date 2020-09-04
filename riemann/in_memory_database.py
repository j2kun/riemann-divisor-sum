'''A simple in-memory divisor database.'''
from dataclasses import dataclass
from typing import List

from riemann.database import DivisorDb
from riemann.database import RiemannDivisorSum
from riemann.database import SummaryStats


@dataclass
class InMemoryDivisorDb(DivisorDb):
    def __init__(self):
        self.data = dict()

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
