from riemann.counterexample_search import best_witness
from riemann.divisor import divisor_sum
import time

# so numba can compile it
divisor_sum(10)

start = time.time()
best_witness(100000)
end = time.time()
print(end - start)
