import React, { useState, useEffect } from 'react';

function PlaySong() {
  const [songs, setSongs] = useState([]); // State for song options
  const [selectedSong, setSelectedSong] = useState(''); // State for the selected song
  const [bpm, setBpm] = useState(120); // State for BPM input
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error state
  const [submissionMessage, setSubmissionMessage] = useState(''); // Message after submission

  // Fetch songs from an API or server
  useEffect(() => {
    const fetchSongs = async () => {
      setLoading(true); // Start loading
      try {
        // Simulate API call (Replace with your actual API endpoint)
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
        setSubmissionMessage('Song and BPM submitted successfully!');
        console.log('Submitted:', { selectedSong, bpm });
      } else {
        throw new Error('Failed to submit song and BPM.');
      }
    } catch (error) {
      setSubmissionMessage('Error submitting: ' + error.message);
    }
  };

  const handleStop = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/done_song', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ song: selectedSong, bpm: parseInt(bpm, 10) })
      });

      if (response.ok) {
        setSubmissionMessage('Song stopped successfully!');
        console.log('Song stopped');
      } else {
        throw new Error('Failed to stop the song.');
      }
    } catch (error) {
      setSubmissionMessage('Error stopping the song: ' + error.message);
    }
  };

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h1>Play Song</h1>
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
    </div>
  );
}

export default PlaySong;
