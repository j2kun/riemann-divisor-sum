from functools import reduce
from numba import jit
from numba import njit
from riemann.primes import primes
from riemann.types import Partition
from riemann.types import PrimeFactorization
from riemann.types import RiemannDivisorSum
from typing import List
import math


@njit
def partitions_of_n(n: int) -> List[Partition]:
    '''Compute all partitions of an integer n.'''
    p = [0] * n
    k = 0
    output = []
    p[k] = n

    while True:
        output.append([x for x in p if x != 0])

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

    return output


@njit
def partition_to_prime_factorization(
        partition: Partition) -> PrimeFactorization:
    return [(primes[i], exp) for (i, exp) in enumerate(partition)]


@njit
def prime_factor_divisor_sum(prime_factors: PrimeFactorization) -> int:
    '''Compute the sum of divisors of a positive integer
    expressed in its prime factorization.'''
    if not prime_factors:
        return 1

    divisor_sum = 1
    for (prime, exponent) in prime_factors:
        divisor_sum *= int((prime**(exponent + 1) - 1) / (prime - 1))

    return divisor_sum


def compute_riemann_divisor_sum(
        factorization: PrimeFactorization) -> RiemannDivisorSum:
    '''Compute a divisor sum.'''
    n = reduce(lambda x, y: x * y, (p**a for (p, a) in factorization))
    ds = prime_factor_divisor_sum(factorization)
    wv = ds / (n * math.log(math.log(n)))
    return RiemannDivisorSum(n=n, divisor_sum=ds, witness_value=wv)
