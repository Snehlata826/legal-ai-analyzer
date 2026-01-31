function FileUploader({ onFileSelect }) {
  return (
    <input
      type="file"
      accept=".pdf"
      onChange={(e) => onFileSelect(e.target.files[0])}
    />
  );
}

export default FileUploader;
