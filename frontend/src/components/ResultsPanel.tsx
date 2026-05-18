import React from "react";
import type { EntropyResponse } from "../types";

interface ResultsPanelProps {
  result: EntropyResponse;
}

function formatNumber(value: number): string {
  return value.toFixed(4);
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

function ResultsPanel({ result }: ResultsPanelProps) {
  return (
    <section className="results">
      <div className="result-card result-card--main">
        <span>Главный результат</span>
        <h2>H(A,B) = {formatNumber(result.jointSystem.entropy)} бит</h2>
        <p>
          Для независимых систем энтропии складываются:
          неопределенность сложной системы равна сумме неопределенностей подсистем.
        </p>

        <div className="result-card__meta">
          <div>
            <small>Количество состояний</small>
            <strong>{result.jointSystem.statesCount}</strong>
          </div>

          <div>
            <small>Hmax(A,B)</small>
            <strong>{formatNumber(result.jointSystem.maxEntropy)}</strong>
          </div>

          <div>
            <small>Perplexity</small>
            <strong>{formatNumber(result.jointSystem.perplexity)}</strong>
          </div>
        </div>
      </div>

      <div className="results-grid">
        <article className="metric-card metric-card--accent">
          <span>Система A</span>
          <strong>{formatNumber(result.systemA.entropy)} бит</strong>
          <small>H(A), состояний: {result.systemA.statesCount}</small>
        </article>

        <article className="metric-card metric-card--accent">
          <span>Система B</span>
          <strong>{formatNumber(result.systemB.entropy)} бит</strong>
          <small>H(B), состояний: {result.systemB.statesCount}</small>
        </article>

        <article className="metric-card">
          <span>Hmax(A)</span>
          <strong>{formatNumber(result.systemA.maxEntropy)}</strong>
          <small>log₂({result.systemA.statesCount})</small>
        </article>

        <article className="metric-card">
          <span>Hmax(B)</span>
          <strong>{formatNumber(result.systemB.maxEntropy)}</strong>
          <small>log₂({result.systemB.statesCount})</small>
        </article>

        <article className="metric-card">
          <span>Избыточность A</span>
          <strong>{formatPercent(result.systemA.redundancy)}</strong>
          <small>1 - H(A) / Hmax(A)</small>
        </article>

        <article className="metric-card">
          <span>Избыточность B</span>
          <strong>{formatPercent(result.systemB.redundancy)}</strong>
          <small>1 - H(B) / Hmax(B)</small>
        </article>

        <article className="metric-card">
          <span>Перплексия A</span>
          <strong>{formatNumber(result.systemA.perplexity)}</strong>
          <small>эффективное число состояний</small>
        </article>

        <article className="metric-card">
          <span>Перплексия B</span>
          <strong>{formatNumber(result.systemB.perplexity)}</strong>
          <small>эффективное число состояний</small>
        </article>
      </div>
    </section>
  );
}

export default ResultsPanel;