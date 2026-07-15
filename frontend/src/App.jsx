import React, { useState, useEffect } from 'react';
import api from './utils/api';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(api.isAuthenticated());

  const handleLogin = () => setIsAuthenticated(true);
  const handleLogout = () => {
    api.logout();
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return <Dashboard onLogout={handleLogout} />;
}
