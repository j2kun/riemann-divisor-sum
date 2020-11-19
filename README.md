# Divisor Sums for the Riemann Hypothesis

An application that glibly searches for RH counterexamples,
while also teaching software engineering principles.

Blog posts:

- https://jeremykun.com/2020/09/11/searching-for-rh-counterexamples-setting-up-pytest/
- https://jeremykun.com/2020/09/11/searching-for-rh-counterexamples-adding-a-database/
- https://jeremykun.com/2020/09/28/searching-for-rh-counterexamples-search-strategies/

## Development requirements

Requires

- [GMP](https://gmplib.org/) for arbitrary precision arithmetic
- [gmpy2](https://gmpy2.readthedocs.io/en/latest/intro.html) for Python GMP bindings
- postgres and/or sqlite3

On Mac OS X these can be installed via brew as follows

```
brew install gmp mpfr libmpc postgresql
```

Then, in a virtualenv,

```
pip install gmpy2
```

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
