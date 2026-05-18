import React from "react";

interface JointMatrixProps {
  matrix: number[][];
}

function JointMatrix({ matrix }: JointMatrixProps) {
  const flatValues = matrix.flat();
  const maxValue = Math.max(...flatValues, 0.000001);

  return (
    <section className="card matrix-card">
      <div className="section-heading">
        <span className="eyebrow">Совместное распределение</span>
        <h2>Матрица P(Ai, Bj)</h2>
        <p>
          Так как системы независимы, каждая ячейка считается как произведение
          вероятностей соответствующих состояний: P(Ai, Bj) = P(Ai) · P(Bj).
        </p>
      </div>

      <div className="matrix-wrapper">
        <table className="matrix-table">
          <thead>
            <tr>
              <th className="matrix-corner">A \ B</th>
              {matrix[0]?.map((_, columnIndex) => (
                <th key={`b-${columnIndex}`}>B{columnIndex + 1}</th>
              ))}
            </tr>
          </thead>

          <tbody>
            {matrix.map((row, rowIndex) => (
              <tr key={`row-${rowIndex}`}>
                <th>A{rowIndex + 1}</th>

                {row.map((value, columnIndex) => {
                  const intensity = 0.14 + (value / maxValue) * 0.74;

                  return (
                    <td
                      key={`cell-${rowIndex}-${columnIndex}`}
                      style={{
                        backgroundColor: `rgba(56, 189, 248, ${intensity})`
                      }}
                    >
                      <strong>{value.toFixed(4)}</strong>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="matrix-note">
        Чем ярче ячейка, тем больше совместная вероятность пары состояний.
      </div>
    </section>
  );
}

export default JointMatrix;