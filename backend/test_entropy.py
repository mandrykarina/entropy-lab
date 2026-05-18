import pytest
from fastapi.testclient import TestClient

from entropy_service import (
    calculate_all_metrics,
    calculate_entropy,
    calculate_joint_matrix,
    calculate_max_entropy,
    calculate_perplexity,
    calculate_redundancy,
    validate_probabilities,
)
from main import app


client = TestClient(app)


def assert_matrix_close(actual: list[list[float]], expected: list[list[float]]) -> None:
    """Compare two matrices with pytest.approx for float values."""
    assert len(actual) == len(expected)

    for actual_row, expected_row in zip(actual, expected):
        assert len(actual_row) == len(expected_row)

        for actual_value, expected_value in zip(actual_row, expected_row):
            assert actual_value == pytest.approx(expected_value)


# ----------------------------
# Entropy core tests
# ----------------------------

def test_entropy_for_single_certain_state_is_zero() -> None:
    assert calculate_entropy([1.0]) == pytest.approx(0.0)


def test_entropy_for_uniform_binary_distribution_is_one() -> None:
    assert calculate_entropy([0.5, 0.5]) == pytest.approx(1.0)


def test_entropy_for_uniform_four_state_distribution_is_two() -> None:
    assert calculate_entropy([0.25, 0.25, 0.25, 0.25]) == pytest.approx(2.0)


def test_entropy_with_zero_probability_contribution_is_zero() -> None:
    assert calculate_entropy([0.0, 1.0]) == pytest.approx(0.0)


def test_complex_entropy_for_two_uniform_binary_systems() -> None:
    result = calculate_all_metrics([0.5, 0.5], [0.5, 0.5])

    assert result["systemA"]["entropy"] == pytest.approx(1.0)
    assert result["systemB"]["entropy"] == pytest.approx(1.0)
    assert result["jointSystem"]["entropy"] == pytest.approx(2.0)


def test_complex_entropy_with_deterministic_system() -> None:
    result = calculate_all_metrics([1.0, 0.0], [0.5, 0.5])

    assert result["systemA"]["entropy"] == pytest.approx(0.0)
    assert result["systemB"]["entropy"] == pytest.approx(1.0)
    assert result["jointSystem"]["entropy"] == pytest.approx(1.0)


def test_joint_matrix_for_independent_systems() -> None:
    actual = calculate_joint_matrix(
        probabilities_a=[0.5, 0.5],
        probabilities_b=[0.25, 0.75],
    )

    expected = [
        [0.125, 0.375],
        [0.125, 0.375],
    ]

    assert_matrix_close(actual, expected)


def test_max_entropy_for_four_states_is_two() -> None:
    assert calculate_max_entropy(4) == pytest.approx(2.0)


def test_perplexity_for_entropy_two_is_four() -> None:
    assert calculate_perplexity(2.0) == pytest.approx(4.0)


def test_redundancy_for_uniform_distribution_is_zero() -> None:
    entropy = calculate_entropy([0.25, 0.25, 0.25, 0.25])
    max_entropy = calculate_max_entropy(4)

    assert calculate_redundancy(entropy, max_entropy) == pytest.approx(0.0)


# ----------------------------
# Validation tests
# ----------------------------

def test_empty_probability_list_raises_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([])


def test_negative_probability_raises_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([0.5, -0.1, 0.6])


def test_probability_greater_than_one_raises_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([1.2, -0.2])


def test_probability_greater_than_one_only_raises_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([1.1, 0.0])


def test_probability_sum_not_equal_to_one_raises_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([0.7, 0.7])


def test_all_zero_probabilities_raise_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([0.0, 0.0])


def test_invalid_states_count_for_max_entropy_raises_error() -> None:
    with pytest.raises(ValueError):
        calculate_max_entropy(0)


# ----------------------------
# API tests
# ----------------------------

def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_calculate_endpoint_with_valid_data_returns_metrics() -> None:
    response = client.post(
        "/calculate",
        json={
            "systemA": [0.5, 0.5],
            "systemB": [0.5, 0.5],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "systemA" in data
    assert "systemB" in data
    assert "jointSystem" in data
    assert "jointMatrix" in data
    assert "explanation" in data

    assert data["systemA"]["entropy"] == pytest.approx(1.0)
    assert data["systemB"]["entropy"] == pytest.approx(1.0)
    assert data["jointSystem"]["entropy"] == pytest.approx(2.0)

    assert_matrix_close(
        data["jointMatrix"],
        [
            [0.25, 0.25],
            [0.25, 0.25],
        ],
    )


def test_calculate_endpoint_with_invalid_probability_sum_returns_error() -> None:
    response = client.post(
        "/calculate",
        json={
            "systemA": [0.7, 0.7],
            "systemB": [0.5, 0.5],
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert "detail" in data
    assert "Сумма вероятностей должна быть равна 1" in data["detail"]


def test_calculate_endpoint_with_empty_distribution_returns_error() -> None:
    response = client.post(
        "/calculate",
        json={
            "systemA": [],
            "systemB": [0.5, 0.5],
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert "detail" in data
    assert "Список вероятностей не должен быть пустым" in data["detail"]


def test_examples_endpoint_returns_predefined_examples() -> None:
    response = client.get("/examples")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 4

    first_example = data[0]

    assert "id" in first_example
    assert "title" in first_example
    assert "description" in first_example
    assert "systemA" in first_example
    assert "systemB" in first_example
    assert "expected" in first_example