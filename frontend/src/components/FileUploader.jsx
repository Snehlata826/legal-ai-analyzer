import React, { useRef } from 'react';

const FileUploader = ({ onFileSelect, isLoading }) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        alert('Please upload a PDF file');
        return;
      }
      onFileSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-uploader">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf"
        style={{ display: 'none' }}
        disabled={isLoading}
      />
      <div className="upload-box" onClick={handleClick}>
        <div className="upload-icon">📄</div>
        <h3>Upload Legal Document</h3>
        <p>Click to select a PDF file</p>
        <p className="upload-hint">PDF files only</p>
      </div>
    </div>
  );
};

export default FileUploader;
