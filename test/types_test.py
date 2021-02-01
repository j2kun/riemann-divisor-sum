from hashlib import sha256
from riemann.types import RiemannDivisorSum
from riemann.types import hash_divisor_sums
import pytest


def test_hash_riemann_divisor_sums():
    sums = [
        RiemannDivisorSum(n=10080, divisor_sum=39312, witness_value=1.75581),
        RiemannDivisorSum(n=10081, divisor_sum=10692, witness_value=0.47749),
        RiemannDivisorSum(n=10082, divisor_sum=15339, witness_value=0.68495),
    ]

    expected = sha256(
        bytes("10080,1.7558,10081,0.4775,10082,0.6849", 'utf-8')).hexdigest()

    assert expected == hash_divisor_sums(sums)
