import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Connect from './pages/Connect';
import DashboardPage from './pages/DashboardPage';
import Home from './pages/Home';
import Pay from './pages/Pay';
import Privacy from './pages/Privacy';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/app" element={<DashboardPage />} />
        <Route path="/pay" element={<Pay />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/connect" element={<Connect />} />
        <Route path="*" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}
