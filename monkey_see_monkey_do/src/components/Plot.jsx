import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Plot() {
  const [results, setResults] = useState([]); // State for result options
  const [selectedResult, setSelectedResult] = useState(''); // State for the selected result
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error state
  const [plotHtml, setPlotHtml] = useState(''); // State to store the plot HTML
  const [submissionMessage, setSubmissionMessage] = useState(''); // Message after submission
  const navigate = useNavigate(); // Initialize the navigate function

  // Fetch results from an API or server
  useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);
      try {
        // Simulate API call (Replace with your actual API endpoint)
        const response = await fetch('http://127.0.0.1:5000/get_all_plots');
        if (!response.ok) {
          throw new Error('Failed to fetch results');
        }
        const data = await response.json(); // Assuming `data` is a list of plot names
        
        setResults(data); // Update state with fetched results
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
    setSubmissionMessage('Loading plot...'); // Show message while fetching plot

    try {
    
      // Fetch the plot HTML from the server based on the selected result
      const response = await fetch(`http://127.0.0.1:5000/get_plot/${selectedResult}`);
      if (!response.ok) {
        throw new Error('Failed to fetch plot');
      }

      const data = await response.text(); // Fetch HTML content
      setPlotHtml(data); // Set the HTML plot content to the state
      setSubmissionMessage('Plot loaded successfully!'); // Update submission message

    } catch (error) {
      setSubmissionMessage('Error during submission: ' + error.message);
    }
  };

  // Handle navigation back to the home page
  const handleBackToHome = () => {
    navigate('/'); // Navigate back to the home page
  };

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h1>View Plots</h1>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="resultDropdown">Select a Result:</label>
        {loading ? (
          <p>Loading plots...</p>
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

      {plotHtml && (
        <div style={{ marginTop: '20px' }}>
          <h2>Plot:</h2>
          {/* Inject the plot HTML */}
          <div dangerouslySetInnerHTML={{ __html: plotHtml }} />
        </div>
      )}

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

      {submissionMessage && <p>{submissionMessage}</p>} {/* Display submission message */}
    </div>
  );
}

export default Plot;
