from functools import reduce
from hypothesis import given
from hypothesis import settings
from riemann.divisor import divisor_sum
from riemann.primes import primes
from riemann.superabundant import partitions_of_n
from riemann.superabundant import prime_factor_divisor_sum
import hypothesis.strategies as st
import pytest


expected_partitions = [
    [[1]],
    [[2], [1, 1]],
    [[3], [2, 1], [1, 1, 1]],
    [[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]],
    [[5], [4, 1], [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]],
]

partition_pairs = zip(range(1,
                            len(expected_partitions) + 1), expected_partitions)

expected_partition_counts = [
    1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135, 176, 231, 297, 385,
    490, 627, 792, 1002, 1255, 1575, 1958, 2436, 3010, 3718, 4565
]

partition_count_pairs = zip(range(1,
                                  len(expected_partition_counts) + 1),
                            expected_partition_counts)


@pytest.mark.parametrize("test_input,expected", partition_pairs)
def test_partitions_of_n(test_input, expected):
    assert partitions_of_n(test_input) == expected


@pytest.mark.parametrize("test_input,expected", partition_count_pairs)
def test_partitions_of_n_size(test_input, expected):
    assert len(partitions_of_n(test_input)) == expected


@st.composite
def prime_factorization(draw):
    '''Draw a random prime factorization.

    This function is a bit finnicky because when the number whose
    prime factorization is chosen here is too large, then the
    test either slows to a crawl (because it's computing a naive
    divisor sum as the ground truth), or it hits an integer max
    value and overflows.
    '''
    indexes = draw(
        st.lists(st.integers(min_value=0, max_value=10),
                 min_size=1,
                 max_size=4,
                 unique=True))
    bases = [primes[i] for i in indexes]
    powers = draw(
        st.lists(st.integers(min_value=1, max_value=3),
                 min_size=len(bases),
                 max_size=len(bases)))
    return list(zip(bases, powers))


@settings(deadline=1000)
@given(prime_factorization())
def test_prime_factor_divisor_sum(prime_factorization):
    n = reduce(lambda x, y: x * y, (p**a for (p, a) in prime_factorization))
    print(n)
    assert prime_factor_divisor_sum(prime_factorization) == divisor_sum(n)


def test_prime_factor_divisor_sum_2():
    assert prime_factor_divisor_sum([(2, 1)]) == divisor_sum(2)


