from riemann.superabundant import partitions_of_n
import pytest


expected_partitions = [
    [[1]],
    [[2], [1, 1]],
    [[3], [2, 1], [1, 1, 1]],
    [[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]],
    [[5], [4, 1], [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]],
]

partition_pairs = zip(
        range(1, len(expected_partitions) + 1),
        expected_partitions)

expected_partition_counts = [
1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135, 176, 231, 297, 385, 490, 627, 792, 1002, 1255, 1575, 1958, 2436, 3010, 3718, 4565
        ]

partition_count_pairs = zip(
        range(1, len(expected_partition_counts) + 1),
        expected_partition_counts)


@pytest.mark.parametrize("test_input,expected", partition_pairs)
def test_partitions_of_n(test_input, expected):
    assert partitions_of_n(test_input) == expected


@pytest.mark.parametrize("test_input,expected", partition_count_pairs)
def test_partitions_of_n_size(test_input, expected):
    assert len(partitions_of_n(test_input)) == expected
