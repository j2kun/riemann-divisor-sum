'''Compute the sum of divisors of a number.'''
from functools import lru_cache


@lru_cache(maxsize=1000000)
def divisor_sum(n: int) -> int:
    '''Compute the sum of divisors of a positive integer.

    Algorithm is described https://math.stackexchange.com/a/22744
    '''
    if n <= 0:
        raise ValueError(
            "Non-positive number {} is not supported.".format(n)
        )

    sign_sequence = [1, 1, -1, -1]

    the_sum = 0
    i = 0
    while True:
        sign = sign_sequence[i % 4]
        x = i // 2 + 1
        if i % 2 == 1:
            x = -x
        arg_diff = int((3 * x * x - x) / 2)

        if n - arg_diff < 0:
           break

        if n - arg_diff == 0:
           the_sum += sign * n
           break

        the_sum += sign * divisor_sum(n - arg_diff)
        i += 1

    return the_sum
