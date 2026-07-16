import React from 'react';

export default function ExecutionLogs({ executions }) {
  const formatTime = (iso) => {
    if (!iso) return '';
    const diff = Date.now() - new Date(iso).getTime();
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="card-glass">
      <div className="flex items-center justify-between mb-3">
        <h3 className="section-title mb-0">Execution Timeline</h3>
        <span className="text-[10px] text-gray-600">{executions.length} total</span>
      </div>

      {executions.length === 0 ? (
        <p className="text-xs text-gray-600 text-center py-6">Awaiting first run</p>
      ) : (
        <div className="space-y-0.5 max-h-[260px] overflow-y-auto">
          {executions.map((exec, idx) => (
            <div key={exec.execution_id || idx} className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[#1a2030] transition-colors">
              <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                exec.status === 'completed' ? 'bg-emerald-400' :
                exec.status === 'failed' ? 'bg-red-400' : 'bg-blue-400 animate-pulse'
              }`} />
              <div className="flex-1 min-w-0">
                <span className="text-xs text-gray-300 capitalize">{exec.trigger_source}</span>
                <span className={`text-[10px] ml-2 font-medium ${
                  exec.status === 'completed' ? 'text-emerald-400' : 'text-red-400'
                }`}>{exec.status}</span>
              </div>
              <div className="text-right flex-shrink-0">
                <p className="text-[10px] text-gray-500">{formatTime(exec.started_at)}</p>
                {exec.duration_seconds && <p className="text-[10px] text-gray-700">{exec.duration_seconds}s</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
