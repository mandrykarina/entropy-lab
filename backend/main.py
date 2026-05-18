from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from entropy_service import calculate_all_metrics


app = FastAPI(
    title="Entropy Lab API",
    description=(
        "API для расчета энтропии сложной системы, состоящей из двух "
        "независимых подсистем."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CalculateRequest(BaseModel):
    systemA: list[float] = Field(
        ...,
        description="Вероятности состояний системы A.",
        examples=[[0.5, 0.25, 0.25]],
    )
    systemB: list[float] = Field(
        ...,
        description="Вероятности состояний системы B.",
        examples=[[0.7, 0.2, 0.1]],
    )


class SystemMetrics(BaseModel):
    probabilities: list[float]
    entropy: float
    maxEntropy: float
    redundancy: float
    perplexity: float
    statesCount: int


class JointSystemMetrics(BaseModel):
    entropy: float
    maxEntropy: float
    redundancy: float
    perplexity: float
    statesCount: int


class EntropyResponse(BaseModel):
    systemA: SystemMetrics
    systemB: SystemMetrics
    jointSystem: JointSystemMetrics
    jointMatrix: list[list[float]]
    explanation: str


class ExampleCase(BaseModel):
    id: str
    title: str
    description: str
    systemA: list[float]
    systemB: list[float]
    expected: EntropyResponse


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/calculate", response_model=EntropyResponse)
def calculate_entropy(request: CalculateRequest) -> dict[str, Any]:
    """
    Calculate entropy metrics for two independent systems.
    """
    try:
        return calculate_all_metrics(request.systemA, request.systemB)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/examples", response_model=list[ExampleCase])
def get_examples() -> list[dict[str, Any]]:
    """
    Return predefined examples for demonstration and manual verification.
    """
    examples = [
        {
            "id": "uniform-binary",
            "title": "Две равномерные бинарные системы",
            "description": (
                "Простой проверочный пример: каждая система имеет два "
                "равновероятных состояния."
            ),
            "systemA": [0.5, 0.5],
            "systemB": [0.5, 0.5],
        },
        {
            "id": "deterministic-and-binary",
            "title": "Детерминированная система и бинарная система",
            "description": (
                "Система A не содержит неопределенности, поэтому H(A) = 0. "
                "Вся неопределенность сложной системы задается системой B."
            ),
            "systemA": [1.0, 0.0],
            "systemB": [0.5, 0.5],
        },
        {
            "id": "uniform-four-and-binary",
            "title": "Равномерная система из 4 состояний и бинарная система",
            "description": (
                "Пример показывает связь максимальной энтропии с количеством "
                "равновероятных состояний."
            ),
            "systemA": [0.25, 0.25, 0.25, 0.25],
            "systemB": [0.5, 0.5],
        },
        {
            "id": "non-uniform-visual",
            "title": "Неравномерные распределения",
            "description": (
                "Пример хорошо подходит для визуализации: вероятности различаются, "
                "а совместная матрица получается более наглядной."
            ),
            "systemA": [0.7, 0.2, 0.1],
            "systemB": [0.5, 0.3, 0.2],
        },
    ]

    result = []

    for example in examples:
        expected = calculate_all_metrics(example["systemA"], example["systemB"])
        result.append(
            {
                **example,
                "expected": expected,
            }
        )

    return result