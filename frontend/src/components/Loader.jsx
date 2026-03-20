import React from 'react';

const STEPS = [
  'Reading document',
  'Extracting clauses',
  'Analysing risks',
  'AI simplification',
  'Finalising',
];

const Loader = ({ message, step }) => (
  <div className="loader-wrap">
    <div className="loader-spinner" />
    <p className="loader-message">{message}</p>

    <div className="loader-steps">
      {STEPS.map((s, i) => (
        <div
          key={i}
          className={`loader-step ${
            i + 1 < step ? 'loader-step--done' :
            i + 1 === step ? 'loader-step--active' : ''
          }`}
        >
          <span className="loader-step-dot" />
          <span className="loader-step-label">{s}</span>
        </div>
      ))}
    </div>
  </div>
);

export default Loader;
