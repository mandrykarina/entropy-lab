import React from "react";

interface DistributionEditorProps {
  title: string;
  statePrefix: string;
  probabilities: number[];
  onChange: (nextProbabilities: number[]) => void;
}

const EPS = 1e-9;

function roundToSix(value: number): number {
  return Number(value.toFixed(6));
}

function getStatus(probabilities: number[]) {
  const sum = probabilities.reduce((acc, value) => acc + value, 0);
  const hasNegative = probabilities.some((value) => value < 0);
  const hasGreaterThanOne = probabilities.some((value) => value > 1);

  if (hasNegative) {
    return {
      type: "error",
      title: "Ошибка",
      text: "Есть отрицательные вероятности"
    };
  }

  if (hasGreaterThanOne) {
    return {
      type: "error",
      title: "Ошибка",
      text: "Вероятность не может быть больше 1"
    };
  }

  if (Math.abs(sum - 1) <= EPS) {
    return {
      type: "success",
      title: "Корректно",
      text: "Сумма равна 1"
    };
  }

  return {
    type: "warning",
    title: "Проверьте сумму",
    text: "Сумма должна быть равна 1"
  };
}

function DistributionEditor({
  title,
  statePrefix,
  probabilities,
  onChange
}: DistributionEditorProps) {
  const sum = probabilities.reduce((acc, value) => acc + value, 0);
  const status = getStatus(probabilities);
  const progressWidth = `${Math.min(Math.abs(sum), 1) * 100}%`;

  function updateProbability(index: number, value: string) {
    const parsedValue = value === "" ? 0 : Number(value);

    const nextProbabilities = probabilities.map((probability, currentIndex) =>
      currentIndex === index ? parsedValue : probability
    );

    onChange(nextProbabilities);
  }

  function addState() {
    onChange([...probabilities, 0]);
  }

  function removeState(index: number) {
    if (probabilities.length === 1) {
      return;
    }

    onChange(probabilities.filter((_, currentIndex) => currentIndex !== index));
  }

  function normalize() {
    const total = probabilities.reduce((acc, value) => acc + value, 0);

    if (total <= 0) {
      return;
    }

    const normalized = probabilities.map((probability) => roundToSix(probability / total));
    const correction = roundToSix(
      1 - normalized.slice(0, -1).reduce((acc, item) => acc + item, 0)
    );

    normalized[normalized.length - 1] = correction;

    onChange(normalized);
  }

  function setUniformDistribution() {
    const value = roundToSix(1 / probabilities.length);
    const nextProbabilities = probabilities.map(() => value);
    const correction = roundToSix(
      1 - nextProbabilities.slice(0, -1).reduce((acc, item) => acc + item, 0)
    );

    nextProbabilities[nextProbabilities.length - 1] = correction;

    onChange(nextProbabilities);
  }

  function setRandomDistribution() {
    const randomValues = probabilities.map(() => Math.random() + 0.05);
    const total = randomValues.reduce((acc, value) => acc + value, 0);

    const nextProbabilities = randomValues.map((value) => roundToSix(value / total));
    const correction = roundToSix(
      1 - nextProbabilities.slice(0, -1).reduce((acc, item) => acc + item, 0)
    );

    nextProbabilities[nextProbabilities.length - 1] = correction;

    onChange(nextProbabilities);
  }

  return (
    <section className="card editor-card">
      <div className="card-header">
        <div>
          <span className="eyebrow">Подсистема {statePrefix}</span>
          <h2>{title}</h2>
        </div>

        <div className={`status status--${status.type}`}>
          <span className="status__dot" />
          <div>
            <strong>{status.title}</strong>
            <small>{status.text}</small>
          </div>
        </div>
      </div>

      <div className="sum-box">
        <div className="sum-box__top">
          <span>Сумма вероятностей</span>
          <strong>{sum.toFixed(6)}</strong>
        </div>

        <div className="sum-track">
          <div
            className={`sum-track__fill sum-track__fill--${status.type}`}
            style={{ width: progressWidth }}
          />
        </div>

        <div className="sum-box__scale">
          <span>0</span>
          <span>цель: 1</span>
        </div>
      </div>

      <div className="probability-list">
        {probabilities.map((probability, index) => (
          <div className="probability-row" key={`${statePrefix}-${index}`}>
            <label htmlFor={`${statePrefix}-${index}`}>
              <span>{statePrefix}{index + 1}</span>
              <small>состояние {index + 1}</small>
            </label>

            <input
              id={`${statePrefix}-${index}`}
              type="number"
              min="-1"
              max="1"
              step="0.01"
              value={Number.isNaN(probability) ? "" : probability}
              onChange={(event) => updateProbability(index, event.target.value)}
            />

            <button
              className="icon-button"
              type="button"
              onClick={() => removeState(index)}
              disabled={probabilities.length === 1}
              title="Удалить состояние"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <div className="button-grid">
        <button className="button" type="button" onClick={addState}>
          + Состояние
        </button>

        <button className="button" type="button" onClick={normalize}>
          Нормализовать
        </button>

        <button className="button" type="button" onClick={setUniformDistribution}>
          Равномерно
        </button>

        <button className="button" type="button" onClick={setRandomDistribution}>
          Случайно
        </button>
      </div>
    </section>
  );
}

export default DistributionEditor;