'''A simple in-memory divisor database.'''
from datetime import datetime
from typing import List

from dataclasses import replace
from riemann.database import DivisorDb
from riemann.types import RiemannDivisorSum
from riemann.types import SearchBlockState
from riemann.types import SearchMetadata
from riemann.types import SummaryStats
from riemann.types import hash_divisor_sums


class InMemoryDivisorDb(DivisorDb):
    def __init__(self):
        self.data = dict()
        self.metadata = dict()

    def load(self) -> List[RiemannDivisorSum]:
        return list(self.data.values())

    def load_metadata(self) -> List[SearchMetadata]:
        return list(self.metadata.values())

    def initialize_schema(self):
        pass

    def insert_search_blocks(self, blocks: List[SearchMetadata]) -> None:
        already_processed_pks = set(self.metadata.keys())
        proposed_pks = set([x.key() for x in blocks])
        duplicates = already_processed_pks & proposed_pks

        if duplicates:
            raise ValueError(f"PK violation for key values={duplicates}")

        for block in blocks:
            block = replace(block, state=SearchBlockState.NOT_STARTED)
            self.metadata[block.key()] = block

    def claim_next_search_block(self,
                                search_index_type: str) -> SearchMetadata:
        eligible = [
            x for x in self.metadata.values()
            if x.state == SearchBlockState.NOT_STARTED
        ]
        chosen = min(eligible, key=lambda metadata: metadata.creation_time)
        chosen = replace(
            chosen,
            state=SearchBlockState.IN_PROGRESS,
            start_time=datetime.now(),
        )
        self.metadata[chosen.key()] = chosen
        return chosen

    def finish_search_block(self, metadata: SearchMetadata,
                            divisor_sums: List[RiemannDivisorSum]) -> None:
        block_hash = hash_divisor_sums(divisor_sums)
        block = replace(
            metadata,
            state=SearchBlockState.FINISHED,
            end_time=datetime.now(),
            block_hash=block_hash,
        )
        self.metadata[block.key()] = block
        for divisor_sum in divisor_sums:
            if divisor_sum.witness_value > self.THRESHOLD_WITNESS_VALUE:
                self.data[divisor_sum.n] = divisor_sum

    def summarize(self) -> SummaryStats:
        if not self.data:
            return SummaryStats(largest_computed_n=None,
                                largest_witness_value=None)

        largest_computed_n = max(self.data.values(), key=lambda x: x.n)
        largest_witness_value = max(self.data.values(),
                                    key=lambda x: x.witness_value)

        return SummaryStats(largest_computed_n=largest_computed_n,
                            largest_witness_value=largest_witness_value)
