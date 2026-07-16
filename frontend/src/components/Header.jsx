import React from 'react';

export default function Header({ onLogout, onTrigger, triggering, status }) {
  return (
    <header className="border-b border-[#27272a] bg-[#09090b] sticky top-0 z-50">
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-white">
              <svg className="w-4 h-4 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-sm font-semibold text-white">PULSE</h1>
            </div>
          </div>

          {/* Center - Status */}
          <div className="hidden md:flex items-center gap-2">
            <span className="status-dot-active" />
            <span className="text-xs text-[#71717a]">
              Agent Active
            </span>
            <span className="text-xs text-[#3f3f46]">·</span>
            <span className="text-xs text-[#71717a]">
              Next run {status?.next_run ? new Date(status.next_run).toLocaleTimeString('en-US', {hour:'numeric', minute:'2-digit', hour12:true}) : '7:00 AM'}
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={onTrigger}
              disabled={triggering}
              className="btn-primary text-xs flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {triggering ? (
                <>
                  <svg className="animate-spin w-3 h-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Running...
                </>
              ) : (
                'Run Agent'
              )}
            </button>

            <button onClick={onLogout} className="btn-secondary text-xs px-3 py-2">
              Sign out
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
