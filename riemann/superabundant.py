from collections import defaultdict
from functools import reduce
from typing import Dict
from typing import List
from typing import Tuple

from gmpy2 import divexact
from gmpy2 import log
from gmpy2 import mpz
from numba import njit
from riemann.primes import primes
from riemann.types import Partition
from riemann.types import PrimeFactorization
from riemann.types import RiemannDivisorSum


@njit
def partitions_of_n(
    n: int,
    start: int = None,
    stop: int = None,
) -> List[Tuple[int, Partition]]:
    '''Compute all partitions of an integer n.

    If start is provided, return only the subset of partitions starting from
    that index.

    If stop is provided, return only the subset of partitions up to (and
    including) that index.

    Returns a list of tuples (index, partition).
    '''

    # this could possibly be further improved by allowing the user to pass in
    # the partition to "start" the enumeration from, which would require me to
    # thread it through from the search_strategy, and also figure out how to
    # choose k here, and set index=start.
    p = [0] * n
    k = 0
    output = []
    p[k] = n
    index = 0

    while True:
        if (
            (start is None or start <= index) and
            (stop is None or index <= stop)
        ):
            output.append((index, [x for x in p if x != 0]))

        if stop is not None and stop <= index:
            break

        right_of_non_one = 0
        while k >= 0 and p[k] == 1:
            right_of_non_one += 1
            k -= 1

        if k < 0:
            # partition is all 1s
            break

        p[k] -= 1
        amount_to_split = right_of_non_one + 1
        while amount_to_split > p[k]:
            p[k + 1] = p[k]
            amount_to_split -= p[k]
            k += 1
        p[k + 1] = amount_to_split
        k += 1
        index += 1

    return output


@njit
def count_partitions_of_n(n: int) -> int:
    '''Compute the number of partitions of n.'''
    p = [0] * n
    k = 0
    count = 0
    p[k] = n

    while True:
        count += 1

        right_of_non_one = 0
        while k >= 0 and p[k] == 1:
            right_of_non_one += 1
            k -= 1

        if k < 0:
            # partition is all 1s
            break

        p[k] -= 1
        amount_to_split = right_of_non_one + 1
        while amount_to_split > p[k]:
            p[k + 1] = p[k]
            amount_to_split -= p[k]
            k += 1
        p[k + 1] = amount_to_split
        k += 1

    return count


@njit
def partition_to_prime_factorization(
        partition: Partition) -> PrimeFactorization:
    return [(primes[i], exp) for (i, exp) in enumerate(partition)]


def factorize(n: mpz, primes: List[int]) -> PrimeFactorization:
    assert n > 0
    factorization: Dict[int, int] = defaultdict(int)
    for p in primes:
        while n % p == 0:
            factorization[p] += 1
            n = divexact(n, p)
    return [(k, factorization[k]) for k in primes]


def prime_factor_divisor_sum(prime_factors: PrimeFactorization) -> int:
    '''Compute the sum of divisors of a positive integer
    expressed in its prime factorization.'''
    if not prime_factors:
        return 1

    divisor_sum = mpz(1)
    for (prime, exponent) in prime_factors:
        divisor_sum *= int((mpz(prime)**(exponent + 1) - 1) / (prime - 1))

    return divisor_sum


def compute_riemann_divisor_sum(
        factorization: PrimeFactorization) -> RiemannDivisorSum:
    '''Compute a divisor sum.'''
    n = reduce(lambda x, y: x * y, (mpz(p)**a for (p, a) in factorization))
    ds = prime_factor_divisor_sum(factorization)
    wv = ds / (n * log(log(n)))
    return RiemannDivisorSum(n=n, divisor_sum=ds, witness_value=wv)


class CachedPartitionsOfN:
    '''
    This class mimics a list containing the full list of partitions of an
    integer n, but only stores one continguous sublist of the complete set at
    any given time. It optimizes for forward sequential access using
    __getitem__, because when there is a cache miss, it loads forward by
    max_cache_size.
    '''

    def __init__(self, n, max_cache_size=1000000):
        self.n = n
        self.cache = None
        self.max_cache_size = max_cache_size
        self.len = count_partitions_of_n(n=n)

    def _update_cache_starting_at(self, index):
        self.cache = dict(partitions_of_n(
            n=self.n,
            start=index,
            stop=index+self.max_cache_size,
        ))

    def __getitem__(self, index):
        if self.cache is None or index not in self.cache:
            self._update_cache_starting_at(index)

        return self.cache[index]

    def __len__(self):
        return self.len
