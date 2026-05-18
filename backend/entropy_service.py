from __future__ import annotations

import math
from typing import Any


EPS = 1e-9
ROUND_DIGITS = 12


def _round_float(value: float) -> float:
    """Round float values to make API output stable and readable."""
    return round(value, ROUND_DIGITS)


def validate_probabilities(probabilities: list[float]) -> None:
    """
    Validate that a list represents a correct probability distribution.

    Requirements:
    - list is not empty;
    - all values are finite numbers;
    - probabilities are in [0, 1];
    - not all probabilities are zero;
    - sum of probabilities is equal to 1 with EPS tolerance.
    """
    if not probabilities:
        raise ValueError("Список вероятностей не должен быть пустым.")

    for index, probability in enumerate(probabilities, start=1):
        if not math.isfinite(probability):
            raise ValueError(f"Вероятность #{index} должна быть конечным числом.")

        if probability < 0:
            raise ValueError(f"Вероятность #{index} не может быть отрицательной.")

        if probability > 1:
            raise ValueError(f"Вероятность #{index} не может быть больше 1.")

    total = sum(probabilities)

    if abs(total) <= EPS:
        raise ValueError("Все вероятности не могут быть равны нулю.")

    if abs(total - 1.0) > EPS:
        raise ValueError(
            f"Сумма вероятностей должна быть равна 1. "
            f"Текущее значение: {total:.12g}."
        )


def normalize_probabilities(probabilities: list[float]) -> list[float]:
    """
    Normalize a non-empty list of non-negative probabilities.

    This function is useful when the frontend sends values whose sum is not 1.
    Example:
    [2, 3, 5] -> [0.2, 0.3, 0.5]
    """
    if not probabilities:
        raise ValueError("Список вероятностей не должен быть пустым.")

    for index, probability in enumerate(probabilities, start=1):
        if not math.isfinite(probability):
            raise ValueError(f"Вероятность #{index} должна быть конечным числом.")

        if probability < 0:
            raise ValueError(f"Вероятность #{index} не может быть отрицательной.")

    total = sum(probabilities)

    if abs(total) <= EPS:
        raise ValueError("Нельзя нормализовать список, сумма которого равна нулю.")

    return [_round_float(probability / total) for probability in probabilities]


def calculate_entropy(probabilities: list[float]) -> float:
    """
    Calculate Shannon entropy:

    H(X) = -Σ p_i * log2(p_i)

    If p_i = 0, its contribution is considered equal to 0.
    """
    validate_probabilities(probabilities)

    entropy = 0.0

    for probability in probabilities:
        if probability > 0:
            entropy -= probability * math.log2(probability)

    return _round_float(entropy)


def calculate_max_entropy(states_count: int) -> float:
    """
    Calculate maximum entropy for a system with n states:

    Hmax(X) = log2(n)
    """
    if states_count < 1:
        raise ValueError("Количество состояний должно быть хотя бы 1.")

    return _round_float(math.log2(states_count))


def calculate_redundancy(entropy: float, max_entropy: float) -> float:
    """
    Calculate redundancy:

    redundancy = 1 - H / Hmax

    If Hmax = 0, redundancy is returned as 0 to avoid division by zero.
    This case corresponds to a system with only one possible state.
    """
    if max_entropy < 0:
        raise ValueError("Максимальная энтропия не может быть отрицательной.")

    if abs(max_entropy) <= EPS:
        return 0.0

    redundancy = 1.0 - entropy / max_entropy

    return _round_float(redundancy)


def calculate_perplexity(entropy: float) -> float:
    """
    Calculate perplexity:

    perplexity = 2^H

    Perplexity can be interpreted as the effective number of equally probable states.
    """
    if entropy < -EPS:
        raise ValueError("Энтропия не может быть отрицательной.")

    return _round_float(2**entropy)


def calculate_joint_matrix(
    probabilities_a: list[float],
    probabilities_b: list[float],
) -> list[list[float]]:
    """
    Calculate joint probability matrix for two independent systems:

    P(Ai, Bj) = P(Ai) * P(Bj)
    """
    validate_probabilities(probabilities_a)
    validate_probabilities(probabilities_b)

    return [
        [_round_float(probability_a * probability_b) for probability_b in probabilities_b]
        for probability_a in probabilities_a
    ]


def _calculate_system_metrics(probabilities: list[float]) -> dict[str, Any]:
    """Calculate entropy-related metrics for one probability distribution."""
    entropy = calculate_entropy(probabilities)
    max_entropy = calculate_max_entropy(len(probabilities))
    redundancy = calculate_redundancy(entropy, max_entropy)
    perplexity = calculate_perplexity(entropy)

    return {
        "probabilities": [_round_float(probability) for probability in probabilities],
        "entropy": entropy,
        "maxEntropy": max_entropy,
        "redundancy": redundancy,
        "perplexity": perplexity,
        "statesCount": len(probabilities),
    }


def calculate_all_metrics(
    probabilities_a: list[float],
    probabilities_b: list[float],
) -> dict[str, Any]:
    """
    Calculate all metrics for two independent systems and their joint system.

    For independent systems:
    H(A, B) = H(A) + H(B)
    """
    validate_probabilities(probabilities_a)
    validate_probabilities(probabilities_b)

    system_a = _calculate_system_metrics(probabilities_a)
    system_b = _calculate_system_metrics(probabilities_b)

    joint_matrix = calculate_joint_matrix(probabilities_a, probabilities_b)

    joint_states_count = len(probabilities_a) * len(probabilities_b)
    joint_entropy = _round_float(system_a["entropy"] + system_b["entropy"])
    joint_max_entropy = calculate_max_entropy(joint_states_count)
    joint_redundancy = calculate_redundancy(joint_entropy, joint_max_entropy)
    joint_perplexity = calculate_perplexity(joint_entropy)

    joint_system = {
        "entropy": joint_entropy,
        "maxEntropy": joint_max_entropy,
        "redundancy": joint_redundancy,
        "perplexity": joint_perplexity,
        "statesCount": joint_states_count,
    }

    explanation = (
        "Для независимых систем совместная вероятность считается как "
        "P(Ai, Bj) = P(Ai) · P(Bj). Поэтому энтропия сложной системы "
        "равна сумме энтропий подсистем: H(A, B) = H(A) + H(B)."
    )

    return {
        "systemA": system_a,
        "systemB": system_b,
        "jointSystem": joint_system,
        "jointMatrix": joint_matrix,
        "explanation": explanation,
    }