import pytest
from riemann.divisor import divisor_sum

def test_sum_of_divisors_of_1():
    assert 1 == divisor_sum(1)

def test_sum_of_divisors_of_72():
    assert 195 == divisor_sum(72)

def test_illegal_input_0():
    with pytest.raises(ValueError):
        divisor_sum(0)

def test_illegal_input_0():
    with pytest.raises(ValueError):
        divisor_sum(0)
def test_illegal_input_negative():
    with pytest.raises(ValueError):
        divisor_sum(-5)
