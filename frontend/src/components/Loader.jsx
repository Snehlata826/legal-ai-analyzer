import React from 'react';

const Loader = ({ message = 'Processing...' }) => {
  return (
    <div className="loader-container">
      <div className="spinner"></div>
      <p className="loader-message">{message}</p>
    </div>
  );
};

export default Loader;
