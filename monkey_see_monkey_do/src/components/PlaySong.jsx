import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import JSZip from 'jszip'; // Import JSZip to handle ZIP files

function PlaySong() {
  const [songs, setSongs] = useState([]); // State for song options
  const [selectedSong, setSelectedSong] = useState(''); // State for the selected song
  const [bpm, setBpm] = useState(120); // State for BPM input
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error state
  const [submissionMessage, setSubmissionMessage] = useState(''); // Message after submission
  const [extractedImages, setExtractedImages] = useState([]); // State for extracted images
  const navigate = useNavigate(); // Initialize the navigate function

  // Fetch songs from an API or server
  useEffect(() => {
    const fetchSongs = async () => {
      setLoading(true); // Start loading
      try {
        const response = await fetch('http://127.0.0.1:5000/get_all_songs');
        if (!response.ok) {
          throw new Error('Failed to fetch songs');
        }
        const data = await response.json(); // Assuming `data` is a list of strings
        setSongs(data); // Update the song list
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false); // End loading
      }
    };

    fetchSongs();
  }, []);

  const handleSongChange = (event) => {
    setSelectedSong(event.target.value); // Update selected song
  };

  const handleBpmChange = (event) => {
    setBpm(event.target.value); // Update BPM
  };

  const handlePlay = async () => {
    if (!selectedSong) {
      alert('Please select a song!');
      return;
    }

    if (!bpm || isNaN(bpm) || bpm <= 0) {
      alert('Please enter a valid BPM value!');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/startsong', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ song: selectedSong, bpm: parseInt(bpm, 10) })
      });

      if (response.ok) {
        setSubmissionMessage('Now Recording!');
        console.log('Submitted:', { selectedSong, bpm });
      } else {
        throw new Error('Failed to submit song and BPM.');
      }
    } catch (error) {
      setSubmissionMessage('Error submitting: ' + error.message);
    }
  };

  const handleStop = async () => {
    setSubmissionMessage('Stopping Recording....');
    try {
      const response = await fetch('http://127.0.0.1:5000/done_song', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ song: selectedSong, bpm: parseInt(bpm, 10) })
      });

      if (!response.ok) {
        throw new Error('Failed to stop the song.');
      }

      const zipBlob = await response.blob(); // Get the ZIP file as a Blob
      const zip = await JSZip.loadAsync(zipBlob); // Load the ZIP file with JSZip

      const imageUrls = [];
      for (const filename of Object.keys(zip.files)) {
        console.log("hi")
        if (filename.endsWith('.png')) { // Process only PNG files
          const fileBlob = await zip.file(filename).async('blob'); // Extract the file as a Blob
          const url = URL.createObjectURL(fileBlob); // Create a URL for the Blob
          imageUrls.push(url);
        }
      }

      setSubmissionMessage('Song recording stopped successfully!');
      console.log('Song stopped, extracted images:', imageUrls);

      // Render the extracted images
      setExtractedImages(imageUrls);
    } catch (error) {
      setSubmissionMessage('Error stopping the song: ' + error.message);
    }
  };

  // Handle navigation back to the home page
  const handleBackToHome = () => {
    navigate('/'); // Navigate back to the home page
  };

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h1>Record Song</h1>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="songDropdown">Select a Song:</label>
        {loading ? (
          <p>Loading songs...</p>
        ) : error ? (
          <p style={{ color: 'red' }}>Error: {error}</p>
        ) : (
          <select
            id="songDropdown"
            value={selectedSong}
            onChange={handleSongChange}
            style={{ marginLeft: '10px', padding: '5px' }}
          >
            <option value="" disabled>
              -- Choose a Song --
            </option>
            {songs.map((song, index) => (
              <option key={index} value={song}>
                {song}
              </option>
            ))}
          </select>
        )}
      </div>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="bpmInput">Enter BPM:</label>
        <input
          id="bpmInput"
          type="number"
          value={bpm}
          onChange={handleBpmChange}
          style={{ marginLeft: '10px', padding: '5px' }}
        />
      </div>
      <button
        onClick={handlePlay}
        style={{
          padding: '10px 20px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          borderRadius: '5px',
          marginRight: '10px'
        }}
        disabled={loading || !!error}
      >
        Play
      </button>
      <button
        onClick={handleStop}
        style={{
          padding: '10px 20px',
          backgroundColor: '#f44336',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          borderRadius: '5px'
        }}
        disabled={loading || !!error}
      >
        Stop
      </button>
      {submissionMessage && <p>{submissionMessage}</p>}

      {/* Render Extracted Images */}
      {extractedImages.length > 0 && (
        <div>
          <h2>Extracted Images:</h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
            {extractedImages.map((url, index) => (
              <img
                key={index}
                src={url}
                alt={`Extracted ${index}`}
                style={{
                  width: '400px',  // Increased width
                  height: 'auto',  // Maintain aspect ratio
                  margin: '10px',
                  border: '1px solid #ccc',
                  borderRadius: '8px',
                }}
              />
            ))}
          </div>
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
    </div>
  );
}

export default PlaySong;
