import React, { useState, useCallback } from 'react';

const RISK = {
  HIGH:   { cls: 'high',   label: 'High risk' },
  MEDIUM: { cls: 'medium', label: 'Medium risk' },
  LOW:    { cls: 'low',    label: 'Low risk' },
};

// Filter out meaningless TF-IDF n-gram artifacts (numbers, stopwords, short tokens)
const STOP_WORDS = new Set([
  'the','of','and','to','in','is','it','at','be','as','or','an','if','on',
  'by','we','us','he','she','they','this','that','with','for','not','from',
  'are','was','were','has','have','had','but','its','our','your','their',
  'all','any','can','may','will','each','both','such','more','also',
]);

function isMeaningfulToken(word) {
  if (!word) return false;
  const clean = word.toLowerCase().replace(/[^a-z]/g, '');
  if (clean.length < 3) return false;
  if (STOP_WORDS.has(clean)) return false;
  // Skip tokens that are purely numeric (e.g. "10 of")
  if (/^\d+$/.test(word.trim())) return false;
  return true;
}

function ClauseCard({ clause, index }) {
  const [expanded, setExpanded] = useState(false);
  const risk = RISK[clause.risk] || RISK.LOW;
  const isML = clause.classifier === 'ml_ensemble';
  const conf = clause.ml_confidence ? Math.round(clause.ml_confidence * 100) : null;

  // Filter to only meaningful SHAP tokens
  const meaningfulAttrs = (clause.attributions || []).filter(
    a => isMeaningfulToken(a.word)
  );
  const inlineTokens = meaningfulAttrs.slice(0, 4);

  const hasProbs = clause.ml_probabilities &&
    Object.keys(clause.ml_probabilities).length > 0;

  const toggle = useCallback(() => setExpanded(v => !v), []);

  return (
    <div className={`clause-card clause-card--${risk.cls}`}>
      <div className="clause-card-inner">

        {/* ── Header ── */}
        <div className="clause-header">
          <span className="clause-index">#{index + 1}</span>

          <span className={`risk-pill risk-pill--${risk.cls}`}>
            {risk.label}
            {conf !== null && (
              <>
                <span className="risk-pill-sep">·</span>
                <span className="risk-pill-conf">{conf}%</span>
              </>
            )}
          </span>

          {!isML && (
            <span className="keyword-mode-tag" title="Install shap + run train_classifier.py for ML mode">
              ⚡ keyword
            </span>
          )}
        </div>

        {/* ── Summary ── */}
        <p className="clause-summary">{clause.simplified}</p>

        {/* ── SHAP tokens (meaningful only) ── */}
        {inlineTokens.length > 0 && (
          <div className="shap-tokens">
            {inlineTokens.map((attr, i) => {
              const val = attr.shap_value ?? (attr.weight ?? 0);
              const isPos = val >= 0;
              return (
                <span
                  key={i}
                  className={`shap-token shap-token--${isPos ? 'pos' : 'neg'}`}
                  title={attr.reason || attr.direction?.replace(/_/g, ' ') || ''}
                >
                  {attr.word}
                  {val !== 0 && (
                    <span className="shap-token-val">
                      {isPos ? '+' : ''}{val.toFixed(2)}
                    </span>
                  )}
                </span>
              );
            })}
          </div>
        )}

        {/* ── Toggle ── */}
        <button className="clause-toggle" onClick={toggle} aria-expanded={expanded}>
          <span className={`toggle-chevron ${expanded ? 'toggle-chevron--open' : ''}`} />
          {expanded ? 'Hide details' : 'See original & explanation'}
        </button>
      </div>

      {/* ── Expanded details ── */}
      {expanded && (
        <div className="clause-details">

          <div>
            <p className="detail-section-label">Original text</p>
            <p className="original-text-block">{clause.original}</p>
          </div>

          <div>
            <p className="detail-section-label">Why this risk level</p>
            <p className="risk-explanation">{clause.explanation}</p>
          </div>

          {/* Probability bars — inside expand only */}
          {hasProbs && (
            <div>
              <p className="detail-section-label">Model confidence</p>
              <div className="prob-bars-compact">
                {['HIGH', 'MEDIUM', 'LOW'].map(label => {
                  const val = clause.ml_probabilities[label] || 0;
                  const pct = Math.round(val * 100);
                  const key = label.toLowerCase();
                  return (
                    <div className="prob-row" key={label}>
                      <span
                        className="prob-label"
                        style={{
                          color: label === 'HIGH' ? 'var(--red)'
                               : label === 'MEDIUM' ? 'var(--amber)'
                               : 'var(--green)',
                        }}
                      >
                        {label}
                      </span>
                      <div className="prob-track">
                        <div
                          className={`prob-fill--${key}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <span className="prob-val">{pct}%</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Full attribution list */}
          {meaningfulAttrs.length > 0 && (
            <div>
              <p className="detail-section-label">
                {clause.shap_method === 'shap'
                  ? 'SHAP feature attributions'
                  : 'Risk keywords detected'}
              </p>
              <ul className="attr-list">
                {meaningfulAttrs.map((attr, i) => {
                  const val = attr.shap_value ?? (attr.weight ?? 0);
                  return (
                    <li key={i} className="attr-item">
                      <span
                        className="attr-word"
                        style={{ color: val >= 0 ? 'var(--red)' : 'var(--green)' }}
                      >
                        "{attr.word}"
                      </span>
                      {val !== 0 && (
                        <span className="attr-val">
                          {val >= 0 ? '+' : ''}{val.toFixed(3)}
                        </span>
                      )}
                      <span className="attr-desc">
                        — {attr.reason || attr.direction?.replace(/_/g, ' ') || ''}
                      </span>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          {/* Entities */}
          {clause.entities && clause.entities.length > 0 && (
            <div>
              <p className="detail-section-label">Identified entities</p>
              <div className="entity-row">
                {clause.entities.map((ent, i) => (
                  <span key={i} className="entity-pill" title={ent.description}>
                    {ent.text}
                    <span className="entity-type-label">{ent.type}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ClauseCard;
