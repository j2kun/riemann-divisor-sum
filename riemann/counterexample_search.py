'''Search for a witness that the Riemann Hypothesis is false.'''
import math
from riemann.divisor import divisor_sum


SEARCH_START = 5041


def witness_value(n: int) -> float:
    denominator = n * math.log(math.log(n))
    return divisor_sum(n) / denominator


def search(max_range: int, search_start: int = SEARCH_START) -> int:
    '''Search for a counterexample to the Riemann Hypothesis.'''
    for n in range(search_start, max_range + 1):
        if witness_value(n) > 1.782:
            return n

    raise ValueError(
        "No witnesses found. "
        "Are you sure trying to disprove RH is wise?")

def best_witness(max_range: int, search_start: int = SEARCH_START) -> int:
    return max(range(search_start, max_range), key=witness_value)
