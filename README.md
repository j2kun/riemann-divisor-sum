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

On Mac OS X this can be installed via brew as follows

```
brew install gmp
brew install mpfr
brew install libmpc
```

Then, in a virtualenv,

```
pip install gmpy2
```
