import React from "react";

interface FormulaBlockProps {
  explanation: string;
}

function FormulaBlock({ explanation }: FormulaBlockProps) {
  return (
    <section className="card formula-card">
      <div className="section-heading">
        <span className="eyebrow">Математическая основа</span>
        <h2>Почему H(A,B) = H(A) + H(B)?</h2>
        <p>
          Энтропия измеряет неопределенность распределения. Если две системы
          независимы, совместное распределение раскладывается в произведение.
        </p>
      </div>

      <div className="formula-grid">
        <div className="formula-item">
          <span>Энтропия системы</span>
          <code>H(X) = -Σ pᵢ log₂(pᵢ)</code>
        </div>

        <div className="formula-item">
          <span>Совместная вероятность</span>
          <code>P(Aᵢ, Bⱼ) = P(Aᵢ) · P(Bⱼ)</code>
        </div>

        <div className="formula-item formula-item--main">
          <span>Независимые системы</span>
          <code>H(A,B) = H(A) + H(B)</code>
        </div>
      </div>

      <div className="proof-box">
        <strong>Короткое доказательство</strong>

        <div className="proof-steps">
          <code>H(A,B) = -ΣΣ pᵢqⱼ log₂(pᵢqⱼ)</code>
          <code>log₂(pᵢqⱼ) = log₂(pᵢ) + log₂(qⱼ)</code>
          <code>H(A,B) = H(A) + H(B)</code>
        </div>

        <p>{explanation}</p>
      </div>
    </section>
  );
}

export default FormulaBlock;