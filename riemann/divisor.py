'''Compute the sum of divisors of a number.'''
import math
from numba import njit


@njit
def divisor_sum(n: int) -> int:
    '''Compute the sum of divisors of a positive integer.'''
    if n <= 0:
        return 0

    i = 1
    limit = math.sqrt(n)
    the_sum = 0
    while i <= limit:
        if n % i == 0:
            the_sum += i
            if i != limit:
                the_sum += n // i
        i += 1

    return the_sum


@njit
def witness_value(n: int) -> float:
    denominator = n * math.log(math.log(n))
    return divisor_sum(n) / denominator
