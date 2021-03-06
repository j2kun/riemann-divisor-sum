from riemann.postgres_database import PostgresDivisorDb
from riemann.search_strategy import SuperabundantSearchStrategy
from riemann.types import SuperabundantEnumerationIndex
import cProfile
import time

db = PostgresDivisorDb(data_source_name='')

samples = 5
search_strategy = SuperabundantSearchStrategy().starting_from(
    SuperabundantEnumerationIndex(71, 196047))
batch = search_strategy.next_batch(250000)

def run_test(batch):
    times = []
    for i in range(samples):
        print(f'Running sample {i}')
        start = time.time()
        db.insert(batch)
        end = time.time()
        print(end - start)
        times.append(end - start)

    return sum(times) / samples


print(run_test(batch))

print("------- cprofile -------")
cProfile.runctx('run_test(batch)', globals(), locals())
