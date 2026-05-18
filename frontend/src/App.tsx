import React, { useEffect, useState } from "react";
import { calculateEntropy, getExamples } from "./api";
import type { EntropyResponse, ExampleCase } from "./types";
import DistributionEditor from "./components/DistributionEditor";
import ResultsPanel from "./components/ResultsPanel";
import ProbabilityBars from "./components/ProbabilityBars";
import JointMatrix from "./components/JointMatrix";
import FormulaBlock from "./components/FormulaBlock";

const EPS = 1e-9;
const AUTO_CALCULATE_DELAY_MS = 450;

function validateDistribution(name: string, probabilities: number[]): string | null {
  if (probabilities.length === 0) {
    return `${name}: список вероятностей не должен быть пустым.`;
  }

  for (let index = 0; index < probabilities.length; index += 1) {
    const probability = probabilities[index];

    if (!Number.isFinite(probability)) {
      return `${name}: вероятность #${index + 1} должна быть конечным числом.`;
    }

    if (probability < 0) {
      return `${name}: вероятность #${index + 1} не может быть отрицательной.`;
    }

    if (probability > 1) {
      return `${name}: вероятность #${index + 1} не может быть больше 1.`;
    }
  }

  const sum = probabilities.reduce((acc, value) => acc + value, 0);

  if (Math.abs(sum) <= EPS) {
    return `${name}: все вероятности не могут быть равны нулю.`;
  }

  if (Math.abs(sum - 1) > EPS) {
    return `${name}: сумма вероятностей должна быть равна 1. Сейчас: ${sum.toFixed(6)}.`;
  }

  return null;
}

function validateInput(systemA: number[], systemB: number[]): string | null {
  return validateDistribution("Система A", systemA) ?? validateDistribution("Система B", systemB);
}

function App() {
  const [systemA, setSystemA] = useState<number[]>([0.5, 0.25, 0.25]);
  const [systemB, setSystemB] = useState<number[]>([0.7, 0.2, 0.1]);

  const [result, setResult] = useState<EntropyResponse | null>(null);
  const [examples, setExamples] = useState<ExampleCase[]>([]);

  const [loading, setLoading] = useState(false);
  const [examplesLoading, setExamplesLoading] = useState(false);
  const [error, setError] = useState("");

  const [autoCalculate, setAutoCalculate] = useState(true);

  async function handleCalculate() {
    const validationError = validateInput(systemA, systemB);

    if (validationError) {
      setResult(null);
      setError(validationError);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await calculateEntropy(systemA, systemB);

      setResult(response);
    } catch (currentError) {
      const message =
        currentError instanceof Error
          ? currentError.message
          : "Не удалось выполнить расчет.";

      setResult(null);
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  function applyExample(example: ExampleCase) {
    setSystemA(example.systemA);
    setSystemB(example.systemB);
    setResult(example.expected);
    setError("");
  }

  useEffect(() => {
    async function loadExamples() {
      try {
        setExamplesLoading(true);

        const loadedExamples = await getExamples();

        setExamples(loadedExamples);
      } catch {
        setExamples([]);
      } finally {
        setExamplesLoading(false);
      }
    }

    loadExamples();
  }, []);

  useEffect(() => {
    handleCalculate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!autoCalculate) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      handleCalculate();
    }, AUTO_CALCULATE_DELAY_MS);

    return () => window.clearTimeout(timeoutId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [systemA, systemB, autoCalculate]);

  return (
    <main className="app">
      <section className="hero">
        <div className="hero__content">
          <div className="badge">Теория информации</div>

          <h1>Entropy Lab</h1>

          <p>
            Расчет энтропии сложной системы из двух независимых подсистем.
          </p>

          <div className="hero__features">
            <span>корректная математика</span>
            <span>наглядная матрица</span>
            <span>проверочные примеры</span>
          </div>
        </div>

        <div className="hero__panel">
          <span className="hero__label">Главная идея</span>
          <strong>H(A, B) = H(A) + H(B)</strong>
          <small>
            Если подсистемы независимы, их неопределенности складываются.
          </small>
        </div>
      </section>

      <section className="grid grid--editors">
        <DistributionEditor
          title="Система A"
          statePrefix="A"
          probabilities={systemA}
          onChange={setSystemA}
        />

        <DistributionEditor
          title="Система B"
          statePrefix="B"
          probabilities={systemB}
          onChange={setSystemB}
        />
      </section>

      <section className="action-panel">
        <div>
          <span className="eyebrow">Управление расчетом</span>
          <h2>Входные вероятности</h2>
          <p>
            В каждой системе сумма вероятностей должна быть равна 1.
            При корректных данных backend рассчитывает энтропию каждой подсистемы,
            совместную энтропию и матрицу P(Ai, Bj).
          </p>
        </div>

        <div className="action-panel__controls">
          <label className="toggle">
            <input
              type="checkbox"
              checked={autoCalculate}
              onChange={(event) => setAutoCalculate(event.target.checked)}
            />
            <span className="toggle__control" />
            <span>Автоматический пересчет</span>
          </label>

          <button
            className="button button--primary"
            onClick={handleCalculate}
            disabled={loading}
            type="button"
          >
            {loading ? "Считаем..." : "Рассчитать"}
          </button>
        </div>
      </section>

      {error && (
        <section className="alert alert--error">
          <strong>Ошибка валидации</strong>
          <span>{error}</span>
        </section>
      )}

      {loading && !result && (
        <section className="card loading-card">
          <div className="loader" />
          <div>
            <strong>Выполняется расчет</strong>
            <p>Frontend отправляет данные в FastAPI backend.</p>
          </div>
        </section>
      )}

      {result && (
        <>
          <ResultsPanel result={result} />

          <section className="grid grid--charts">
            <ProbabilityBars
              title="Распределение системы A"
              statePrefix="A"
              probabilities={result.systemA.probabilities}
            />

            <ProbabilityBars
              title="Распределение системы B"
              statePrefix="B"
              probabilities={result.systemB.probabilities}
            />
          </section>

          <JointMatrix matrix={result.jointMatrix} />

          <FormulaBlock explanation={result.explanation} />
        </>
      )}

      <section className="card examples">
        <div className="section-heading">
          <span className="eyebrow">Проверочные сценарии</span>
          <h2>Готовые примеры</h2>
          <p>
            Карточки ниже нужны для быстрой демонстрации корректности:
            равномерные системы, детерминированный случай и неравномерные распределения.
          </p>
        </div>

        {examplesLoading && (
          <div className="examples-loading">Загружаем примеры из backend...</div>
        )}

        {!examplesLoading && examples.length === 0 && (
          <div className="alert alert--soft">
            Backend недоступен или не вернул проверочные примеры.
          </div>
        )}

        <div className="examples__grid">
          {examples.map((example) => (
            <button
              key={example.id}
              className="example-card"
              type="button"
              onClick={() => applyExample(example)}
            >
              <span>{example.title}</span>
              <p>{example.description}</p>

              <div className="example-card__metrics">
                <small>H(A) = {example.expected.systemA.entropy.toFixed(3)}</small>
                <small>H(B) = {example.expected.systemB.entropy.toFixed(3)}</small>
                <strong>H(A,B) = {example.expected.jointSystem.entropy.toFixed(3)} бит</strong>
              </div>
            </button>
          ))}
        </div>
      </section>

      <footer className="footer">
        Entropy Lab · React + TypeScript + FastAPI · учебный проект по теории информации
      </footer>
    </main>
  );
}

export default App;