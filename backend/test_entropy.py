import math

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


def print_passed(
    title: str,
    what: str,
    input_data: str = "",
    expected: str = "",
) -> None:
    """Print a readable test description for demo recording."""
    print("\n" + "-" * 90)
    print(f"[OK] {title}")
    print(f"Что проверяем: {what}")

    if input_data:
        print(f"Входные данные: {input_data}")

    if expected:
        print(f"Ожидаемый результат: {expected}")

    print("Результат: проверка пройдена")


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

    print_passed(
        title="Математика: энтропия детерминированной системы",
        what="если одно состояние имеет вероятность 1, неопределенности нет",
        input_data="probabilities=[1.0]",
        expected="H=0 бит",
    )


def test_entropy_for_uniform_binary_distribution_is_one() -> None:
    assert calculate_entropy([0.5, 0.5]) == pytest.approx(1.0)

    print_passed(
        title="Математика: энтропия равномерной бинарной системы",
        what="система из двух равновероятных состояний должна иметь энтропию 1 бит",
        input_data="probabilities=[0.5, 0.5]",
        expected="H=1 бит",
    )


def test_entropy_for_uniform_four_state_distribution_is_two() -> None:
    assert calculate_entropy([0.25, 0.25, 0.25, 0.25]) == pytest.approx(2.0)

    print_passed(
        title="Математика: энтропия равномерной системы из 4 состояний",
        what="четыре равновероятных состояния должны давать максимальную энтропию 2 бита",
        input_data="probabilities=[0.25, 0.25, 0.25, 0.25]",
        expected="H=2 бита",
    )


def test_entropy_with_zero_probability_contribution_is_zero() -> None:
    assert calculate_entropy([0.0, 1.0]) == pytest.approx(0.0)

    print_passed(
        title="Математика: обработка нулевой вероятности",
        what="состояние с вероятностью 0 не должно ломать расчет log2(0)",
        input_data="probabilities=[0.0, 1.0]",
        expected="H=0 бит, вклад нулевой вероятности считается равным 0",
    )


def test_complex_entropy_for_two_uniform_binary_systems() -> None:
    result = calculate_all_metrics([0.5, 0.5], [0.5, 0.5])

    assert result["systemA"]["entropy"] == pytest.approx(1.0)
    assert result["systemB"]["entropy"] == pytest.approx(1.0)
    assert result["jointSystem"]["entropy"] == pytest.approx(2.0)

    print_passed(
        title="Математика: свойство H(A,B)=H(A)+H(B)",
        what="для двух независимых систем совместная энтропия должна быть равна сумме энтропий",
        input_data="A=[0.5, 0.5], B=[0.5, 0.5]",
        expected="H(A)=1, H(B)=1, H(A,B)=2",
    )


def test_complex_entropy_with_deterministic_system() -> None:
    result = calculate_all_metrics([1.0, 0.0], [0.5, 0.5])

    assert result["systemA"]["entropy"] == pytest.approx(0.0)
    assert result["systemB"]["entropy"] == pytest.approx(1.0)
    assert result["jointSystem"]["entropy"] == pytest.approx(1.0)

    print_passed(
        title="Математика: сложная система с детерминированной подсистемой",
        what="детерминированная подсистема не должна добавлять неопределенность",
        input_data="A=[1.0, 0.0], B=[0.5, 0.5]",
        expected="H(A)=0, H(B)=1, H(A,B)=1",
    )


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

    print_passed(
        title="Математика: матрица совместных вероятностей",
        what="каждая ячейка должна считаться по формуле P(Ai,Bj)=P(Ai)*P(Bj)",
        input_data="A=[0.5, 0.5], B=[0.25, 0.75]",
        expected="jointMatrix=[[0.125, 0.375], [0.125, 0.375]]",
    )


def test_max_entropy_for_four_states_is_two() -> None:
    assert calculate_max_entropy(4) == pytest.approx(2.0)

    print_passed(
        title="Математика: максимальная энтропия",
        what="максимальная энтропия системы с n состояниями должна считаться как log2(n)",
        input_data="states_count=4",
        expected="Hmax=log2(4)=2",
    )


def test_perplexity_for_entropy_two_is_four() -> None:
    assert calculate_perplexity(2.0) == pytest.approx(4.0)

    print_passed(
        title="Математика: перплексия",
        what="перплексия должна считаться как 2^H",
        input_data="H=2",
        expected="perplexity=2^2=4",
    )


def test_redundancy_for_uniform_distribution_is_zero() -> None:
    entropy = calculate_entropy([0.25, 0.25, 0.25, 0.25])
    max_entropy = calculate_max_entropy(4)

    assert calculate_redundancy(entropy, max_entropy) == pytest.approx(0.0)

    print_passed(
        title="Математика: избыточность равномерного распределения",
        what="если распределение равномерное, энтропия равна максимальной, а избыточность равна 0",
        input_data="probabilities=[0.25, 0.25, 0.25, 0.25]",
        expected="redundancy=1-H/Hmax=0",
    )


# ----------------------------
# Validation tests
# ----------------------------

def test_empty_probability_list_raises_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([])

    print_passed(
        title="Валидация: пустой список вероятностей",
        what="backend не должен принимать систему без состояний",
        input_data="probabilities=[]",
        expected="ValueError: список вероятностей не должен быть пустым",
    )


def test_negative_probability_raises_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([0.5, -0.1, 0.6])

    print_passed(
        title="Валидация: отрицательная вероятность",
        what="вероятность не может быть меньше 0",
        input_data="probabilities=[0.5, -0.1, 0.6]",
        expected="ValueError: вероятность не может быть отрицательной",
    )


def test_probability_greater_than_one_raises_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([1.1, 0.0])

    print_passed(
        title="Валидация: вероятность больше 1",
        what="одно значение вероятности не может быть больше 1",
        input_data="probabilities=[1.1, 0.0]",
        expected="ValueError: вероятность не может быть больше 1",
    )


def test_probability_greater_than_one_is_detected_even_with_other_invalid_values() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([1.2, -0.2])

    print_passed(
        title="Валидация: значения вне диапазона [0,1]",
        what="backend должен отлавливать вероятности, которые выходят за допустимые границы",
        input_data="probabilities=[1.2, -0.2]",
        expected="ValueError: распределение содержит некорректные значения",
    )


def test_probability_sum_not_equal_to_one_raises_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([0.7, 0.7])

    print_passed(
        title="Валидация: сумма вероятностей не равна 1",
        what="сумма всех вероятностей в распределении должна быть равна 1",
        input_data="probabilities=[0.7, 0.7]",
        expected="ValueError: сумма вероятностей должна быть равна 1",
    )


def test_all_zero_probabilities_raise_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([0.0, 0.0])

    print_passed(
        title="Валидация: все вероятности равны нулю",
        what="распределение [0,0] недопустимо, потому что сумма вероятностей равна 0",
        input_data="probabilities=[0.0, 0.0]",
        expected="ValueError: все вероятности не могут быть равны нулю",
    )


def test_invalid_states_count_for_max_entropy_raises_error() -> None:
    with pytest.raises(ValueError):
        calculate_max_entropy(0)

    print_passed(
        title="Валидация: некорректное количество состояний",
        what="для расчета Hmax количество состояний должно быть хотя бы 1",
        input_data="states_count=0",
        expected="ValueError: количество состояний должно быть хотя бы 1",
    )


def test_not_finite_probability_raises_error() -> None:
    with pytest.raises(ValueError):
        validate_probabilities([math.inf, 0.0])

    print_passed(
        title="Валидация: бесконечное значение вероятности",
        what="backend не должен принимать бесконечные или нечисловые значения",
        input_data="probabilities=[inf, 0.0]",
        expected="ValueError: вероятность должна быть конечным числом",
    )


# ----------------------------
# API tests
# ----------------------------

def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    print_passed(
        title="API /health: проверка доступности backend",
        what="endpoint должен быстро подтверждать, что сервер работает",
        input_data="GET /health",
        expected='HTTP 200, {"status": "ok"}',
    )


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

    print_passed(
        title="API /calculate: расчет по корректным данным",
        what="backend должен принять две системы, посчитать энтропии и вернуть jointMatrix",
        input_data='POST /calculate, {"systemA":[0.5,0.5], "systemB":[0.5,0.5]}',
        expected="HTTP 200, H(A)=1, H(B)=1, H(A,B)=2, jointMatrix=[[0.25,0.25],[0.25,0.25]]",
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

    print_passed(
        title="API /calculate: ошибка при некорректной сумме вероятностей",
        what="backend не должен выполнять расчет, если сумма вероятностей в одной из систем не равна 1",
        input_data='POST /calculate, {"systemA":[0.7,0.7], "systemB":[0.5,0.5]}',
        expected="HTTP 400 и сообщение: сумма вероятностей должна быть равна 1",
    )


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

    print_passed(
        title="API /calculate: ошибка при пустом распределении",
        what="backend не должен принимать систему без состояний",
        input_data='POST /calculate, {"systemA":[], "systemB":[0.5,0.5]}',
        expected="HTTP 400 и сообщение: список вероятностей не должен быть пустым",
    )


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

    print_passed(
        title="API /examples: получение проверочных примеров",
        what="backend должен вернуть готовые сценарии, которые frontend использует для быстрой демонстрации",
        input_data="GET /examples",
        expected="HTTP 200, список минимум из 4 примеров, у каждого есть id, title, description, systemA, systemB и expected",
    )