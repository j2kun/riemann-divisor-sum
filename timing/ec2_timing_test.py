from riemann import divisor
from riemann import superabundant
from riemann.search_strategy import SuperabundantSearchStrategy
from riemann.superabundant import partition_to_prime_factorization
from riemann.superabundant import partitions_of_n
from riemann.types import SearchState
from riemann.types import SuperabundantEnumerationIndex
import cProfile
import numba
import time


# allow numba to compile
partition_to_prime_factorization(partitions_of_n(4)[0])
samples = 5


def run_test(search_state_start, batch_size):
    search_strategy = SuperabundantSearchStrategy().starting_from(
        search_state_start)

    times = []
    for i in range(samples):
        start = time.time()
        search_strategy.next_batch(batch_size)
        end = time.time()
        print(end - start)
        times.append(end-start)

    return sum(times) / samples


run_test(SuperabundantEnumerationIndex(71, 196047), 250000)


print("------- cprofile -------")
cProfile.runctx(
    'run_test(SuperabundantEnumerationIndex(71, 196047), 250000)', globals(), locals())
