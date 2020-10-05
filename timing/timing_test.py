from timing import gmpy
from timing import numba
import cProfile
import time


# allow numba to compile
numba.compute_riemann_divisor_sum(
        numba.partition_to_prime_factorization(
            numba.partitions_of_n(4)[1]))


def run_test(module, module_name):
    print(f"---- testing {module_name} ------")
    n = 20
    start = time.time()
    for i in range(30):
        rds = module.compute_riemann_divisor_sum(
                module.partition_to_prime_factorization(
                    module.partitions_of_n(n + i)[200]))
    end = time.time()
    print(end - start)
    return end - start


numba_time = run_test(numba, "numba")
gmpy_time = run_test(gmpy, "gmpy")

print(numba_time / gmpy_time)


print("------- cprofile -------")
cProfile.runctx('run_test(gmpy, "gmpy")', globals(), locals())
