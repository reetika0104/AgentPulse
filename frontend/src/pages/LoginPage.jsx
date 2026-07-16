import React, { useState } from 'react';
import api from '../utils/api';

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.login(username, password);
      onLogin();
    } catch (err) {
      setError(err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm animate-fade-in-up">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-white mb-4">
            <svg className="w-6 h-6 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 className="text-xl font-semibold text-white">PULSE</h1>
          <p className="text-[#71717a] mt-1 text-sm">AI Digital Chief of Staff</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="card-glass space-y-4">
          <div>
            <label htmlFor="username" className="block text-xs font-medium text-[#a1a1aa] mb-1.5">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2.5 bg-[#09090b] border border-[#27272a] rounded-lg
                         text-white placeholder-[#52525b] focus:outline-none focus:border-[#52525b]
                         transition-colors text-sm"
              placeholder="admin"
              required
              autoComplete="username"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-xs font-medium text-[#a1a1aa] mb-1.5">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2.5 bg-[#09090b] border border-[#27272a] rounded-lg
                         text-white placeholder-[#52525b] focus:outline-none focus:border-[#52525b]
                         transition-colors text-sm"
              placeholder="••••••"
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <p className="text-xs text-red-400 text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-2.5 text-sm disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="text-center text-[10px] text-[#3f3f46] mt-6">
          Powered by Amazon Bedrock · AWS
        </p>
      </div>
    </div>
  );
}
