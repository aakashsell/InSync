import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import ViewResults from './components/ViewResults';
import PlaySong from './components/PlaySong';
import UploadPage from './components/UploadPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/viewresults" element={<ViewResults />} />
        <Route path="/playsong" element={<PlaySong />} />
        <Route path="/upload" element={<UploadPage />} />
      </Routes>
    </Router>
  );
}

export default App;
