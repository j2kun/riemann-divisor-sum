from riemann.search_strategy import SuperabundantSearchStrategy
from riemann.types import SuperabundantEnumerationIndex
import tracemalloc

tracemalloc.start()

search_strategy = SuperabundantSearchStrategy().starting_from(
    SuperabundantEnumerationIndex(71, 196047))
batch = search_strategy.next_batch(250000)

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("[ Top 10 ]")
for stat in top_stats[:10]:
    print(stat)
