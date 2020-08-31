'''Compute the sum of divisors of a number.'''

def divisor_sum(n: int) -> int:
    '''Compute the sum of divisors of a positive integer.'''
    if n <= 0:
        raise ValueError(
            "Non-positive number {} is not supported.".format(n)
        )

    return sum(i for i in range(1, n+1) if n%i == 0)
