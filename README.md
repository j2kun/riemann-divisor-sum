# Divisor Sums for the Riemann Hypothesis

[![CircleCI](https://circleci.com/gh/j2kun/riemann-divisor-sum.svg?style=shield)](https://circleci.com/gh/j2kun/riemann-divisor-sum)
[![Coverage Status](https://coveralls.io/repos/github/j2kun/riemann-divisor-sum/badge.svg?branch=main)](https://coveralls.io/github/j2kun/riemann-divisor-sum?branch=main)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/j2kun/riemann-divisor-sum.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/j2kun/riemann-divisor-sum/context:python)

An application that glibly searches for RH counterexamples,
while also teaching software engineering principles.

Blog posts:

- [Setting up Pytest](https://jeremykun.com/2020/09/11/searching-for-rh-counterexamples-setting-up-pytest/)
- [Adding a Database](https://jeremykun.com/2020/09/11/searching-for-rh-counterexamples-adding-a-database/)
- [Search Strategies](https://jeremykun.com/2020/09/28/searching-for-rh-counterexamples-search-strategies/)
- [Unbounded Integers](https://jeremykun.com/2020/10/13/searching-for-rh-counterexamples-unbounded-integers/)
- [Deploying with Docker](https://jeremykun.com/2021/01/04/searching-for-rh-counterexamples-deploying-with-docker/)
- [Performance Profiling](https://jeremykun.com/2021/02/02/searching-for-rh-counterexamples-performance-profiling/)
- [Scaling Up](https://jeremykun.com/2021/02/16/searching-for-rh-counterexamples-scaling-up/)

## Development requirements

Requires Python 3.7 and

- [GMP](https://gmplib.org/) for arbitrary precision arithmetic
- [gmpy2](https://gmpy2.readthedocs.io/en/latest/intro.html) for Python GMP bindings
- postgres

On Mac OS X these can be installed via brew as follows

```
brew install gmp mpfr libmpc postgresql
```

Then, in a virtualenv,

```
pip install -r requrements.txt
```

### Local development with PostgreSQL

For postgres, create a new database cluster
and start the server.

```
initdb --locale=C -E UTF-8 /usr/local/var/postgres
pg_ctl -D /usr/local/var/postgres -l /tmp/logfile start
```

Then create a database like

```
CREATE DATABASE divisor
    WITH OWNER = jeremy;  -- or whatever your username is
```

Then install the pgmp extension using pgxn

```
sudo pip install pgxnclient
pgxn install pgmp
pgxn load -d divisor pgmp
```

Note you may need to add the location of `gmp.h` to `$C_INCLUDE_PATH`
so that the build step for `pgmp` can find it.
This appears to be a problem mostly on Mac OSX.
See https://github.com/dvarrazzo/pgmp/issues/4 if you run into issues.

```bash
# your version may be different than 6.2.0. Find it by running
# brew info gmp
export C_INCLUDE_PATH="/usr/local/Cellar/gmp/6.2.0/include:$C_INCLUDE_PATH"
```

In this case, you may also want to build pgmp from source,

```bash
git clone https://github.com/j2kun/pgmp && cd pgmp
make
sudo make install
```

## Running the program

```bash
python -m riemann.populate_database --help
usage: populate_database.py [-h] [--data_source_name DATA_SOURCE_NAME]
                            [--search_strategy_name {ExhaustiveSearchStrategy,SuperabundantSearchStrategy}]
                            [--batch_size BATCH_SIZE]

optional arguments:
  -h, --help            show this help message and exit
  --data_source_name DATA_SOURCE_NAME
                        The psycopg data_source_name string
  --search_strategy_name {ExhaustiveSearchStrategy,SuperabundantSearchStrategy}
                        The search strategy name
  --batch_size BATCH_SIZE
                        The size of search batches
```

## Deploying with Docker

Running with docker removes the need to install postgres and dependencies.

### Locally

```bash
docker build -t divisordb -f divisordb.Dockerfile .
docker build -t divisorsearch -f divisorsearch.Dockerfile .

docker run -d --name divisordb -p 5432:5432 divisordb:latest

# The host address for the divisordb container is nested inside a json
# `jq` is a CLI for stream processing json data.
export PGHOST=$(docker network inspect bridge | jq -r '.[0].Containers[] | select(.Name=="divisordb") | .IPv4Address' | sed 's|/.*$||g')

docker run -d --name divisorsearch --env PGHOST=$PGHOST divisorsearch:latest
```

#### Manual inspection

After the `divisordb` container is up, you can test whether it's working by

```
pg_isready -d divisor -h $PGHOST -p 5432 -U docker
```

or by going into the container and checking the database manually

```
$ docker exec -it divisordb /bin/bash
# now inside the container
$ psql
divisor=# \d   # \d is postgres for 'describe tables'

              List of relations
 Schema |        Name        | Type  | Owner
--------+--------------------+-------+--------
 public | riemanndivisorsums | table | docker
 public | searchmetadata     | table | docker
(2 rows)
```

#### On EC2

```bash
# install docker, see get.docker.com
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# log out and log back in

git clone https://github.com/j2kun/riemann-divisor-sum && cd riemann-divisor-sum
bash deploy.sh
```
