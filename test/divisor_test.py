from riemann.divisor import compute_riemann_divisor_sums
from riemann.divisor import divisor_sum
from riemann.divisor import witness_value
from riemann.types import RiemannDivisorSum
import pytest

# sigma(n), starting at n=1
divisor_sums = [
    1, 3, 4, 7, 6, 12, 8, 15, 13, 18, 12, 28, 14, 24, 24, 31, 18, 39, 20, 42,
    32, 36, 24, 60, 31, 42, 40, 56, 30, 72, 32, 63, 48, 54, 48, 91, 38, 60, 56,
    90, 42, 96, 44, 84, 78, 72, 48, 124, 57, 93, 72
]

input_output_pairs = zip(range(1, len(divisor_sums) + 1), divisor_sums)


@pytest.mark.parametrize("test_input,expected", input_output_pairs)
def test_sum_of_divisors(test_input, expected):
    assert divisor_sum(test_input) == expected


def test_sum_of_divisors_of_1():
    assert 1 == divisor_sum(1)


def test_sum_of_divisors_of_72():
    assert 195 == divisor_sum(72)


def test_witness_value():
    assert abs(witness_value(10080) - 1.755814) < 1e-5


def test_witness_value_precomputed_ds():
    assert abs(witness_value(10080, 1) - (1 / 22389.61097)) < 1e-5


def test_compute_riemann_divisor_sums():
    expected = [
        RiemannDivisorSum(n=10080, divisor_sum=39312, witness_value=1.75581),
        RiemannDivisorSum(n=10081, divisor_sum=10692, witness_value=0.47749),
        RiemannDivisorSum(n=10082, divisor_sum=15339, witness_value=0.68495),
    ]

    actual = compute_riemann_divisor_sums(start_n=10080, end_n=10081)

    for ex, ac in zip(expected, actual):
        assert ex.approx_equal(ac)
