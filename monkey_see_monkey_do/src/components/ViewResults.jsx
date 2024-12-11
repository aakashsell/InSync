import React, { useState, useEffect } from 'react';
import JSZip from 'jszip';

function ViewResults() {
  const [results, setResults] = useState([]); // State for result options
  const [selectedResult, setSelectedResult] = useState(''); // State for the selected result
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error state
  const [images, setImages] = useState([]); // State for extracted images
  const [submissionMessage, setSubmissionMessage] = useState(''); // Message after submission

  // Fetch results from an API or server
  useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);
      try {
        // Simulate API call (Replace with your actual API endpoint)
        const response = await fetch('http://127.0.0.1:5000/get_all_results');
        if (!response.ok) {
          throw new Error('Failed to fetch results');
        }
        const data = await response.json(); // Assuming `data` is a list of strings
        setResults(data); // Update the results list
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, []);

  const handleResultChange = (event) => {
    setSelectedResult(event.target.value);
  };

  const handleSubmit = async () => {
    if (!selectedResult) {
      alert('Please select a result!');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/get_result', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body:  selectedResult,
      });

      if (!response.ok) {
        throw new Error('Failed to fetch the ZIP file');
      }

      const zipBlob = await response.blob(); // Get ZIP file as a blob
      const zip = await JSZip.loadAsync(zipBlob); // Unzip the blob
      const extractedImages = [];

      // Extract images from the ZIP file
      for (const filename in zip.files) {
        if (filename.endsWith('.png') || filename.endsWith('.jpg') || filename.endsWith('.jpeg')) {
          const file = zip.files[filename];
          const content = await file.async('blob'); // Extract as a blob
          const url = URL.createObjectURL(content); // Create a URL for the image
          extractedImages.push(url);
        }
      }

      setImages(extractedImages); // Update the state with image URLs
      setSubmissionMessage('Images successfully extracted and displayed!');
    } catch (error) {
      setSubmissionMessage('Error during submission: ' + error.message);
    }
  };

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h1>View Results</h1>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="resultDropdown">Select a Result:</label>
        {loading ? (
          <p>Loading results...</p>
        ) : error ? (
          <p style={{ color: 'red' }}>Error: {error}</p>
        ) : (
          <select
            id="resultDropdown"
            value={selectedResult}
            onChange={handleResultChange}
            style={{ marginLeft: '10px', padding: '5px' }}
          >
            <option value="" disabled>
              -- Choose a Result --
            </option>
            {results.map((result, index) => (
              <option key={index} value={result}>
                {result}
              </option>
            ))}
          </select>
        )}
      </div>
      <button
        onClick={handleSubmit}
        style={{
          padding: '10px 20px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          borderRadius: '5px',
        }}
        disabled={loading || !!error}
      >
        Submit
      </button>
      {submissionMessage && <p>{submissionMessage}</p>}

      {/* Display the extracted images */}
      {images.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h2>Extracted Images:</h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
            {images.map((image, index) => (
              <img
                key={index}
                src={image}
                alt={`Extracted ${index}`}
                style={{
                  width: '300px',
                  height: '450px',
                  margin: '10px',
                  border: '1px solid #ccc',
                }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ViewResults;
