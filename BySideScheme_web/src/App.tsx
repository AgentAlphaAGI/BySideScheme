import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Advisor from './pages/Advisor';
import Memory from './pages/Memory';
import Profile from './pages/Profile';
import Simulator from './pages/Simulator';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="advisor" element={<Advisor />} />
          <Route path="simulator" element={<Simulator />} />
          <Route path="memory" element={<Memory />} />
          <Route path="profile" element={<Profile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
