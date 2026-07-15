import React from 'react';

export default function ExecutionLogs({ executions }) {
  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-emerald-400/10 text-emerald-400">Completed</span>;
      case 'running':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-blue-400/10 text-blue-400 animate-pulse">Running</span>;
      case 'failed':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-red-400/10 text-red-400">Failed</span>;
      default:
        return <span className="px-2 py-0.5 text-xs rounded-full bg-gray-400/10 text-gray-400">{status}</span>;
    }
  };

  const formatTime = (isoString) => {
    if (!isoString) return 'N/A';
    try {
      const date = new Date(isoString);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="card animate-slide-up">
      <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
        Execution Logs
      </h3>

      {executions.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-4">No executions yet</p>
      ) : (
        <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
          {executions.map((exec, idx) => (
            <div
              key={exec.execution_id || idx}
              className="flex items-center justify-between p-2.5 bg-gray-800/50 rounded-lg"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  {getStatusBadge(exec.status)}
                  <span className="text-xs text-gray-500">{exec.trigger_source}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1 truncate">
                  {formatTime(exec.started_at)}
                </p>
              </div>
              {exec.duration_seconds && (
                <span className="text-xs text-gray-600 ml-2">
                  {exec.duration_seconds}s
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
