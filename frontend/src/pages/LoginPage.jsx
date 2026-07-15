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
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 mb-5 shadow-[0_0_60px_rgba(99,102,241,0.3)] animate-float">
            <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 className="text-3xl font-black gradient-text tracking-tight">PULSE</h1>
          <p className="text-gray-500 mt-2 text-sm">Personal Unified Life & Productivity Executive</p>
          <p className="text-[10px] text-gray-600 mt-1 uppercase tracking-widest">AI Digital Chief of Staff</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="card-glass space-y-5">
          <div>
            <label htmlFor="username" className="block text-xs font-medium text-gray-400 mb-2">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-white/[0.03] border border-white/[0.08] rounded-xl
                         text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500/50
                         focus:ring-1 focus:ring-indigo-500/30 transition-all text-sm"
              placeholder="Enter username"
              required
              autoComplete="username"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-xs font-medium text-gray-400 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-white/[0.03] border border-white/[0.08] rounded-xl
                         text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500/50
                         focus:ring-1 focus:ring-indigo-500/30 transition-all text-sm"
              placeholder="Enter password"
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="p-3 bg-red-500/5 border border-red-500/20 rounded-xl text-red-400 text-xs text-center">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-3 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Authenticating...
              </span>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-8 text-center space-y-2">
          <p className="text-[10px] text-gray-600">
            Powered by Amazon Bedrock • EventBridge • Lambda • CloudWatch
          </p>
          <div className="flex items-center justify-center gap-2">
            <div className="status-dot-active" />
            <span className="text-[10px] text-gray-500">Agent Active — Next run at 7:00 AM</span>
          </div>
        </div>
      </div>
    </div>
  );
}
