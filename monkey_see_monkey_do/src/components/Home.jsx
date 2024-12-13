import '../App.css';
import { useNavigate } from 'react-router-dom';

function App() {
  const navigate = useNavigate();

  const handleClick = (button) => {
    switch (button) {
      case 1:
        navigate('/playsong');
        break;
      case 2:
        navigate('/upload');  // Navigate to the upload page
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
        <button onClick={() => handleClick(1)}>Record</button>
        <button onClick={() => handleClick(2)}>Upload</button>
        <button onClick={() => handleClick(3)}>View Results</button>
      </div>
    </div>
  );
}

export default App;
