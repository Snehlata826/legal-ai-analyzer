import React, { useState } from 'react';
import { evaluateDocument } from '../api';

const MIN_CLAUSES_FOR_EVAL = 10;

function EvaluatePanel({ requestId, hasResults, clauseCount = 0 }) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const runEval = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await evaluateDocument(requestId);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!hasResults) {
    return (
      <div className="eval-empty">
        <div className="eval-empty-icon">📊</div>
        <p>Upload and analyse a document first.</p>
      </div>
    );
  }

  if (!data && !loading) {
    return (
      <div className="eval-empty">
        <div className="eval-empty-icon">🔬</div>
        <p>Compare the ML classifier against keyword and TF-IDF baselines.</p>
        <button
          className="btn btn--purple"
          style={{ marginTop: 20 }}
          onClick={runEval}
        >
          Run evaluation
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="eval-empty">
        <div style={{
          width: 34, height: 34,
          border: '2.5px solid var(--border)',
          borderTopColor: 'var(--purple)',
          borderRadius: '50%',
          animation: 'spin .8s linear infinite',
          margin: '0 auto',
        }} />
        <p style={{ marginTop: 14 }}>Running evaluation…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="eval-empty">
        <p style={{ color: 'var(--red)' }}>⚠ {error}</p>
        <button className="btn btn--ghost" style={{ marginTop: 14 }} onClick={runEval}>
          Retry
        </button>
      </div>
    );
  }

  const { evaluation, shap_explanations, metadata } = data;
  const ml      = evaluation.ml_model;
  const summary = evaluation.comparison_summary;
  const tooFew  = evaluation.n_clauses < MIN_CLAUSES_FOR_EVAL;

  return (
    <div className="eval-panel">

      {/* Small-dataset warning */}
      {tooFew && (
        <div className="eval-small-dataset">
          <span>⚠</span>
          <span>
            Only <strong>{evaluation.n_clauses} clauses</strong> — evaluation metrics
            are unreliable on small documents. Upload a larger contract for meaningful
            comparison. The 100% scores you may see reflect memorisation, not
            real generalisation.
          </span>
        </div>
      )}

      {/* Headline — single F1 metric + rerun */}
      <div className="eval-headline">
        <div className="eval-headline-top">
          <h3 className="eval-headline-title">Evaluation report</h3>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <span className="eval-headline-meta">
              {evaluation.n_clauses} clauses · {evaluation.ground_truth_source}
            </span>
            <button
              className="btn btn--ghost"
              style={{ padding: '6px 12px', fontSize: '.78rem' }}
              onClick={runEval}
            >
              ↻ Re-run
            </button>
          </div>
        </div>

        <div className="eval-metrics-row">
          {[
            { label: 'Macro F1',  value: `${(ml.macro_f1 * 100).toFixed(1)}%`,         sub: 'main metric' },
            { label: 'Accuracy',  value: `${(ml.accuracy * 100).toFixed(1)}%`,          sub: 'ML ensemble' },
            { label: 'Precision', value: `${(ml.macro_precision * 100).toFixed(1)}%`,   sub: 'macro avg' },
            { label: 'Recall',    value: `${(ml.macro_recall * 100).toFixed(1)}%`,      sub: 'macro avg' },
          ].map(m => (
            <div className="eval-metric" key={m.label}>
              <p className="eval-metric-label">{m.label}</p>
              <p className="eval-metric-value">{m.value}</p>
              <p className="eval-metric-sub">{m.sub}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Method comparison table */}
      <div className="eval-table-card">
        <div className="eval-table-header">
          <span className="eval-table-title">Method comparison</span>
          <span className="eval-headline-meta">sorted by macro F1</span>
        </div>
        <table>
          <thead>
            <tr>
              <th style={{ width: '38%' }}>Method</th>
              <th>Accuracy</th>
              <th>Macro F1</th>
              <th>Precision</th>
              <th>Recall</th>
            </tr>
          </thead>
          <tbody>
            {summary.map((row, i) => {
              const isML = row.method.includes('ML') || row.method.includes('Ensemble');
              return (
                <tr key={row.method} className={i === 0 ? 'row--best' : ''}>
                  <td>
                    <span className={isML ? 'method-ml' : 'method-other'}>
                      <span className={`m-dot ${isML ? 'm-dot--ml' : 'm-dot--kw'}`} />
                      {row.method}
                      {i === 0 && <span className="best-star">best</span>}
                    </span>
                  </td>
                  <td className="mono">{(row.accuracy * 100).toFixed(1)}%</td>
                  <td className="mono">{(row.macro_f1 * 100).toFixed(1)}%</td>
                  <td className="mono">{(row.macro_prec * 100).toFixed(1)}%</td>
                  <td className="mono">{(row.macro_rec * 100).toFixed(1)}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Per-class metrics */}
      <div>
        <p style={{
          fontSize: '.72rem', fontWeight: 600,
          textTransform: 'uppercase', letterSpacing: '.6px',
          color: 'var(--text-3)', marginBottom: 10,
        }}>
          Per-class metrics — ML ensemble
        </p>
        <div className="per-class-grid">
          {['HIGH', 'MEDIUM', 'LOW'].map(label => {
            const m = ml.per_class?.[label];
            if (!m) return null;
            return (
              <div className="per-class-card" key={label}>
                <p className={`per-class-heading per-class-heading--${label.toLowerCase()}`}>
                  {label} risk
                </p>
                {[
                  ['Precision', m.precision],
                  ['Recall',    m.recall],
                  ['F1 score',  m.f1],
                ].map(([name, val]) => (
                  <div className="per-class-row" key={name}>
                    <span className="per-class-metric">{name}</span>
                    <span className="per-class-val">{(val * 100).toFixed(1)}%</span>
                  </div>
                ))}
                <div className="per-class-row" style={{ marginTop: 4, borderTop: '1px solid var(--border)', paddingTop: 6 }}>
                  <span className="per-class-metric">Support</span>
                  <span className="per-class-val">{m.support}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Confusion matrix */}
      {ml.confusion_matrix && (
        <div className="eval-table-card">
          <div className="eval-table-header">
            <span className="eval-table-title">Confusion matrix</span>
            <span className="eval-headline-meta">rows = true · cols = predicted</span>
          </div>
          <table>
            <thead>
              <tr>
                <th style={{ width: 120 }}>True \ Pred</th>
                {ml.confusion_matrix.labels.map(l => <th key={l}>{l}</th>)}
              </tr>
            </thead>
            <tbody>
              {ml.confusion_matrix.matrix.map((row, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600, color: 'var(--text-2)' }}>
                    {ml.confusion_matrix.labels[i]}
                  </td>
                  {row.map((val, j) => (
                    <td
                      key={j}
                      className={`mono ${i === j ? 'cm-diag' : val > 0 ? 'cm-off' : 'cm-zero'}`}
                    >
                      {val}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* SHAP attributions */}
      {shap_explanations?.length > 0 && !shap_explanations[0]?.error && (
        <div>
          <p style={{
            fontSize: '.72rem', fontWeight: 600,
            textTransform: 'uppercase', letterSpacing: '.6px',
            color: 'var(--text-3)', marginBottom: 10,
            display: 'flex', alignItems: 'center', gap: 8,
          }}>
            SHAP attributions per clause
            {!metadata?.shap_available && (
              <span style={{
                fontSize: '.68rem', color: 'var(--amber)',
                background: 'var(--amber-bg)', padding: '1px 8px',
                borderRadius: 10, fontWeight: 500,
                textTransform: 'none', letterSpacing: 0,
              }}>
                keyword fallback · install shap for real scores
              </span>
            )}
          </p>
          <div className="shap-clause-list">
            {(() => {
              // Annotate each explanation with its filtered tokens
              const annotated = shap_explanations.slice(0, 12).map((exp, originalIndex) => ({
                exp,
                originalIndex,
                tokens: (exp.top_features || [])
                  .filter(f => f.word && f.word.replace(/[^a-z]/g, '').length >= 3)
                  .slice(0, 6),
              }));

              const withKeywords = annotated.filter(x => x.tokens.length > 0);
              const emptyCount   = annotated.length - withKeywords.length;

              return (
                <>
                  {withKeywords.map(({ exp, originalIndex, tokens }) => {
                    const riskCls = exp.predicted_label?.toLowerCase() || 'low';
                    return (
                      <div className="shap-clause-card" key={originalIndex}>
                        <div className="shap-clause-row">
                          <span className="clause-index">#{originalIndex + 1}</span>
                          <span className={`risk-pill risk-pill--${riskCls}`}>
                            {exp.predicted_label}
                            <span className="risk-pill-sep">·</span>
                            <span className="risk-pill-conf">
                              {Math.round((exp.confidence || 0) * 100)}%
                            </span>
                          </span>
                          {exp.method === 'shap' && (
                            <span style={{
                              fontSize: '.65rem', color: 'var(--purple)',
                              background: 'var(--purple-bg)', padding: '1px 7px',
                              borderRadius: 10, fontWeight: 600,
                            }}>
                              SHAP
                            </span>
                          )}
                        </div>
                        <div className="shap-features">
                          {tokens.map((f, j) => {
                            const v = f.shap_value ?? 0;
                            return (
                              <span
                                key={j}
                                className={`shap-token shap-token--${v >= 0 ? 'pos' : 'neg'}`}
                                title={f.direction?.replace(/_/g, ' ') || ''}
                              >
                                {f.word}
                                {v !== 0 && (
                                  <span className="shap-token-val">
                                    {v >= 0 ? '+' : ''}{v.toFixed(2)}
                                  </span>
                                )}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}

                  {emptyCount > 0 && (
                    <p style={{
                      fontSize: '.78rem',
                      color: 'var(--text-4)',
                      padding: '6px 2px',
                      fontStyle: 'italic',
                    }}>
                      {emptyCount} clause{emptyCount !== 1 ? 's' : ''} had no significant keywords detected.
                    </p>
                  )}
                </>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}

export default EvaluatePanel;
