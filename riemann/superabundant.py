from dataclasses import dataclass
from numba import njit
from typing import Dict
from typing import List


@dataclass(frozen=True)
class PossiblySuperabundantNumber:
    prime_factors: Dict[int, int]


@njit
def partitions_of_n(n: int) -> List[List[int]]:
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
