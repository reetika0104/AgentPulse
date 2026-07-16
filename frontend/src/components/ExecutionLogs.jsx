import React from 'react';

export default function ExecutionLogs({ executions }) {
  const formatTime = (isoString) => {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      const now = new Date();
      const diff = now - date;
      if (diff < 60000) return 'Just now';
      if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return '';
    }
  };

  return (
    <div className="card-glass">
      <div className="flex items-center justify-between mb-4">
        <h3 className="section-title mb-0">Execution Timeline</h3>
        <span className="text-[10px] text-[#52525b]">{executions.length} runs</span>
      </div>

      {executions.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-xs text-[#52525b]">No executions yet</p>
          <p className="text-[10px] text-[#3f3f46] mt-1">Click "Run Agent" to trigger</p>
        </div>
      ) : (
        <div className="space-y-1 max-h-[280px] overflow-y-auto">
          {executions.map((exec, idx) => (
            <div
              key={exec.execution_id || idx}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[#27272a]/50 transition-colors"
            >
              <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                exec.status === 'completed' ? 'bg-emerald-500' :
                exec.status === 'failed' ? 'bg-red-500' : 'bg-blue-500 animate-pulse'
              }`} />

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#a1a1aa] capitalize">{exec.trigger_source}</span>
                  <span className={`text-[10px] font-medium ${
                    exec.status === 'completed' ? 'text-emerald-400' :
                    exec.status === 'failed' ? 'text-red-400' : 'text-blue-400'
                  }`}>
                    {exec.status}
                  </span>
                </div>
              </div>

              <div className="text-right flex-shrink-0">
                <p className="text-[10px] text-[#52525b]">{formatTime(exec.started_at)}</p>
                {exec.duration_seconds && (
                  <p className="text-[10px] text-[#3f3f46]">{exec.duration_seconds}s</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
