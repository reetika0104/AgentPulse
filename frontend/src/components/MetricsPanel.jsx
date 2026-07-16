import React from 'react';

export default function MetricsPanel({ metrics, executions }) {
  const totalRuns = metrics?.total_runs || executions?.length || 0;
  const successRate = metrics?.success_rate || (totalRuns > 0 ? 100 : 0);
  const avgDuration = metrics?.avg_duration_seconds || 0;
  const streak = metrics?.streak || 0;

  return (
    <div className="card-glass">
      <h3 className="section-title">Performance</h3>

      <div className="grid grid-cols-2 gap-3">
        <MetricBox label="Total Runs" value={totalRuns} />
        <MetricBox label="Success Rate" value={`${successRate}%`} />
        <MetricBox label="Avg Duration" value={avgDuration ? `${avgDuration}s` : '—'} />
        <MetricBox label="Streak" value={streak} />
      </div>

      <div className="flex items-center gap-2 mt-4 pt-3 border-t border-[#27272a]">
        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
        <span className="text-[10px] text-[#52525b]">
          CloudWatch · PULSE/Agent
        </span>
      </div>
    </div>
  );
}

function MetricBox({ label, value }) {
  return (
    <div className="p-3 rounded-lg bg-[#27272a]/50">
      <p className="text-[10px] text-[#71717a] uppercase tracking-wider mb-1">{label}</p>
      <p className="text-lg font-semibold text-white">{value}</p>
    </div>
  );
}
