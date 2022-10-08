from functools import reduce

from gmpy2 import mpz
from hypothesis import given
from hypothesis import settings
from riemann.divisor import divisor_sum
from riemann.primes import primes
from riemann.superabundant import CachedPartitionsOfN
from riemann.superabundant import compute_riemann_divisor_sum
from riemann.superabundant import count_partitions_of_n
from riemann.superabundant import factorize
from riemann.superabundant import partitions_of_n
from riemann.superabundant import prime_factor_divisor_sum
import hypothesis.strategies as st
import pytest

expected_partitions = [
    list(enumerate([[1]])),
    list(enumerate([[2], [1, 1]])),
    list(enumerate([[3], [2, 1], [1, 1, 1]])),
    list(enumerate([[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]])),
    list(enumerate([[5], [4, 1], [3, 2], [3, 1, 1], [
         2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]])),
    list(enumerate([
        [6], [5, 1], [4, 2], [4, 1, 1], [3, 3], [3, 2, 1],
        [3, 1, 1, 1],  [2, 2, 2],  [2, 2, 1, 1], [2, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1]
    ])),
]

partition_pairs = zip(
    range(1, len(expected_partitions) + 1),
    expected_partitions,
)

expected_partition_counts = [
    1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135, 176, 231, 297, 385,
    490, 627, 792, 1002, 1255, 1575, 1958, 2436, 3010, 3718, 4565
]

partition_count_pairs = zip(
    range(1, len(expected_partition_counts) + 1),
    expected_partition_counts
)


@pytest.mark.parametrize("test_input,expected", partition_pairs)
def test_partitions_of_n(test_input, expected):
    assert partitions_of_n(test_input) == expected


@settings(deadline=10000)
@given(
    st.integers(min_value=7, max_value=50),
)
def test_partitions_of_n_sums_to_n(n):
    for _, partition in partitions_of_n(n=n):
        assert sum(partition) == n


@pytest.mark.parametrize("test_input,expected", partition_count_pairs)
def test_partitions_of_n_size(test_input, expected):
    assert len(partitions_of_n(test_input)) == expected


@pytest.mark.parametrize("n", list(range(5, 20)))
def test_count_partitions_of_n_size(n):
    assert count_partitions_of_n(n) == len(partitions_of_n(n))


def test_partitions_of_n_sublist_start():
    full_list_5 = list(enumerate(
        [[5], [4, 1], [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]]))
    assert partitions_of_n(n=5, start=2) == full_list_5[2:]


def test_partitions_of_n_sublist_stop():
    full_list_5 = list(enumerate(
        [[5], [4, 1], [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]]))
    assert partitions_of_n(n=5, stop=3) == full_list_5[:4]


def test_partitions_of_n_sublist_start_and_stop():
    full_list_5 = list(enumerate(
        [[5], [4, 1], [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]]))
    assert partitions_of_n(n=5, start=2, stop=4) == full_list_5[2:5]


@given(
    st.integers(min_value=5, max_value=20),
    st.integers(min_value=10, max_value=100000)
)
def test_partitions_of_n_cached(n, max_cache_size):
    # for some of these tests, 10 > total number of partitions, and for some it
    # is less, and the cache is needed.
    expected_partitions = partitions_of_n(n=n)
    actual_partitions = CachedPartitionsOfN(n=n, max_cache_size=max_cache_size)

    for i in range(len(expected_partitions)):
        assert expected_partitions[i][1] == actual_partitions[i]


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


@settings(deadline=10000)
@given(prime_factorization())
def test_prime_factor_divisor_sum(prime_factorization):
    n = reduce(lambda x, y: x * y, (p**a for (p, a) in prime_factorization))
    print(n)
    assert prime_factor_divisor_sum(prime_factorization) == divisor_sum(n)


@given(prime_factorization())
def test_factorize(prime_factorization):
    n = reduce(lambda x, y: x * y, (mpz(p)**a for (p, a) in prime_factorization))
    primes = [x[0] for x in prime_factorization]
    assert prime_factorization == factorize(n, primes)


def test_prime_factor_divisor_sum_2():
    assert prime_factor_divisor_sum([(2, 1)]) == divisor_sum(2)


def test_mpz_too_large_to_convert_to_float():
    # Regression test for issues/14
    factorization = [
        (2, 3), (3, 3), (5, 3), (7, 3), (11, 3), (13, 3), (17, 3), (19, 3),
        (23, 3), (29, 3), (31, 3), (37, 3), (41, 3), (43, 3), (47, 3), (53, 3),
        (59, 3), (61, 3), (67, 3), (71, 3), (73, 3), (79, 3), (83, 3), (89, 3),
        (97, 3), (101, 3), (103, 3), (107, 3), (109, 2), (113, 2), (127, 2),
        (131, 2), (137, 2), (139, 1), (149, 1), (151, 1), (157, 1), (163, 1),
        (167, 1), (173, 1), (179, 1), (181, 1), (191, 1), (193, 1), (197, 1),
        (199, 1), (211, 1), (223, 1), (227, 1), (229, 1), (233, 1), (239, 1),
        (241, 1), (251, 1), (257, 1), (263, 1), (269, 1), (271, 1), (277, 1),
        (281, 1), (283, 1), (293, 1), (307, 1), (311, 1), (313, 1), (317, 1),
        (331, 1), (337, 1), (347, 1), (349, 1), (353, 1), (359, 1), (367, 1),
        (373, 1), (379, 1), (383, 1), (389, 1), (397, 1), (401, 1), (409, 1),
        (419, 1), (421, 1), (431, 1), (433, 1), (439, 1), (443, 1), (449, 1),
        (457, 1), (461, 1), (463, 1), (467, 1), (479, 1), (487, 1), (491, 1),
        (499, 1), (503, 1), (509, 1), (521, 1), (523, 1), (541, 1), (547, 1),
        (557, 1), (563, 1), (569, 1), (571, 1), (577, 1), (587, 1)
    ]

    # no assertion because we're checking that no overflow error occurs
    compute_riemann_divisor_sum(factorization)
