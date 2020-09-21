from dataclasses import dataclass


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

