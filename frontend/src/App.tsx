import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SessionPage from './pages/SessionPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SessionPage />} />
        <Route path="/s/:token" element={<SessionPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;