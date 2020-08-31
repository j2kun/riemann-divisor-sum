from riemann.divisor import divisor_sum

def test_sum_of_divisors_of_72():
    assert 195 == divisor_sum(72)
