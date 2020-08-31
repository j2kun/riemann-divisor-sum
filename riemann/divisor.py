'''Compute the sum of divisors of a number.'''

def divisor_sum(n: int) -> int:
    if n <= 0:
        raise ValueError("Non-positive numbers are not supported.")

    return sum(i for i in range(1, n+1) if n%i == 0)
