import '../App.css';
import { useNavigate } from 'react-router-dom';
import { useRef } from 'react';

function App() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null); // Ref for the hidden file input

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log("File selected:", file.name);
      // You can process the file here (e.g., upload to a server)
      const formData = new FormData();
      formData.append('file', file); // Append the file
    
      try {
        const response = await fetch('http://127.0.0.1:5000/upload', {
          method: 'POST',
          body: formData,
          headers: {
            'name' : 'nothiman13'
          }
        });
    
        if (response.ok) {
          console.log("File uploaded successfully!");
        } else {
          console.error("File upload failed.");
        }
      } catch (error) {
        console.error("Error during upload:", error);
      } 
    }
  };

  const handleClick = (button) => {
    switch (button) {
      case 1:
        navigate('/playsong');
        break;
      case 2:
        // Trigger the hidden file input
        fileInputRef.current.click();
        break;
      case 3:
        navigate('/viewresults');
        break;
      default:
        break;
    }
  };

  return (
    <div className="app-container">
      <h1 className="app-title">In Sync</h1>
      <div className="button-group">
        <button onClick={() => handleClick(1)}>Play Song</button>
        <button onClick={() => handleClick(2)}>Upload</button>
        <button onClick={() => handleClick(3)}>View Results</button>
      </div>
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileUpload}
      />
    </div>
  );
}

export default App;
