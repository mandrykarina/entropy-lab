import React from "react";

interface ProbabilityBarsProps {
  title: string;
  statePrefix: string;
  probabilities: number[];
}

function ProbabilityBars({ title, statePrefix, probabilities }: ProbabilityBarsProps) {
  const maxProbability = Math.max(...probabilities, 0.000001);

  return (
    <section className="card probability-card">
      <div className="section-heading">
        <span className="eyebrow">Визуализация</span>
        <h2>{title}</h2>
        <p>
          Горизонтальные бары показывают вклад каждого состояния в распределение.
          Максимальное значение выделяется самой длинной полосой.
        </p>
      </div>

      <div className="bars">
        {probabilities.map((probability, index) => {
          const relativeWidth = Math.max(0, Math.min(probability / maxProbability, 1)) * 100;
          const absoluteWidth = Math.max(0, Math.min(probability, 1)) * 100;

          return (
            <div className="bar-row" key={`${statePrefix}-bar-${index}`}>
              <div className="bar-row__meta">
                <strong>{statePrefix}{index + 1}</strong>
                <span>{probability.toFixed(3)}</span>
              </div>

              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{
                    width: `${relativeWidth}%`
                  }}
                />
              </div>

              <div className="bar-percent">
                <strong>{absoluteWidth.toFixed(1)}%</strong>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default ProbabilityBars;