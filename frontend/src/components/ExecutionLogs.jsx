import React from 'react';

export default function ExecutionLogs({ executions }) {
  const getStatusIndicator = (status) => {
    switch (status) {
      case 'completed':
        return <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.5)]" />;
      case 'running':
        return <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse shadow-[0_0_6px_rgba(99,102,241,0.5)]" />;
      case 'failed':
        return <div className="w-1.5 h-1.5 rounded-full bg-red-400 shadow-[0_0_6px_rgba(248,113,113,0.5)]" />;
      default:
        return <div className="w-1.5 h-1.5 rounded-full bg-gray-600" />;
    }
  };

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

  const getTriggerIcon = (source) => {
    switch (source) {
      case 'scheduler': return '⏰';
      case 'lambda': return 'λ';
      case 'eventbridge': return '📡';
      case 'manual': return '👤';
      default: return '•';
    }
  };

  return (
    <div className="card-glass">
      <div className="flex items-center justify-between mb-4">
        <h3 className="section-title mb-0">Execution Timeline</h3>
        <span className="text-[10px] text-gray-600">{executions.length} runs</span>
      </div>

      {executions.length === 0 ? (
        <div className="text-center py-8">
          <span className="text-2xl opacity-50">⏳</span>
          <p className="text-xs text-gray-500 mt-2">Awaiting first execution</p>
          <p className="text-[10px] text-gray-600 mt-1">Click "Run Agent" to trigger</p>
        </div>
      ) : (
        <div className="space-y-1.5 max-h-[240px] overflow-y-auto pr-1">
          {executions.map((exec, idx) => (
            <div
              key={exec.execution_id || idx}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-white/[0.02] hover:bg-white/[0.04] transition-colors group"
            >
              {/* Timeline dot */}
              <div className="flex flex-col items-center">
                {getStatusIndicator(exec.status)}
                {idx < executions.length - 1 && (
                  <div className="w-px h-3 bg-white/[0.06] mt-1" />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[10px]">{getTriggerIcon(exec.trigger_source)}</span>
                  <span className="text-xs text-gray-300 capitalize">{exec.trigger_source}</span>
                  <span className={`text-[10px] font-medium ${
                    exec.status === 'completed' ? 'text-emerald-400' :
                    exec.status === 'failed' ? 'text-red-400' : 'text-indigo-400'
                  }`}>
                    {exec.status}
                  </span>
                </div>
              </div>

              {/* Right side */}
              <div className="text-right flex-shrink-0">
                <p className="text-[10px] text-gray-500">{formatTime(exec.started_at)}</p>
                {exec.duration_seconds && (
                  <p className="text-[10px] text-gray-600">{exec.duration_seconds}s</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
