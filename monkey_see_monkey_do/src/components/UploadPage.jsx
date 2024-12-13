import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate hook

function UploadPage() {
  const [file, setFile] = useState(null); // State for the selected file
  const [fileName, setFileName] = useState(''); // State for the file name
  const [error, setError] = useState(null); // Error state
  const [successMessage, setSuccessMessage] = useState(''); // Success message after upload
  const navigate = useNavigate(); // Initialize navigate function

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileNameChange = (event) => {
    setFileName(event.target.value);
  };

  const handleUpload = async () => {
    if (!file || !fileName) {
      setError('Please select a file and provide a name!');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('fileName', fileName);

    try {
      const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
        headers: {
          'name': fileName
        }
      });

      if (response.ok) {
        setSuccessMessage('File uploaded successfully!');
        setError(null); // Clear any previous error
      } else {
        throw new Error('Failed to upload file.');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleBackToHome = () => {
    navigate('/'); // Navigate back to home page
  };

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h1>Upload File</h1>
      <div style={{ marginBottom: '20px' }}>
        <input
          type="file"
          onChange={handleFileChange}
          style={{ padding: '5px' }}
        />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="fileName">Enter File Name:</label>
        <input
          id="fileName"
          type="text"
          value={fileName}
          onChange={handleFileNameChange}
          style={{ marginLeft: '10px', padding: '5px' }}
        />
      </div>
      <button
        onClick={handleUpload}
        style={{
          padding: '10px 20px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          borderRadius: '5px',
        }}
      >
        Upload
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}

      {/* Back to Home Button */}
      <div style={{ marginTop: '20px' }}>
        <button
          onClick={handleBackToHome}
          style={{
            padding: '10px 20px',
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            cursor: 'pointer',
            borderRadius: '5px',
            marginLeft: '10px',
          }}
        >
          Back to Home
        </button>
      </div>
    </div>
  );
}

export default UploadPage;
