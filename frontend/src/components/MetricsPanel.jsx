import React from 'react';

export default function MetricsPanel({ metrics, executions }) {
  const totalRuns = metrics?.total_runs || executions?.length || 0;
  const successRate = metrics?.success_rate || (totalRuns > 0 ? 100 : 0);
  const avgDuration = metrics?.avg_duration_seconds || 0;
  const streak = metrics?.streak || 0;

  return (
    <div className="card-glass">
      <h3 className="section-title">Agent Performance</h3>

      <div className="grid grid-cols-2 gap-3">
        <MetricBox
          label="Total Runs"
          value={totalRuns}
          color="text-indigo-400"
          bgColor="bg-indigo-400/5"
        />
        <MetricBox
          label="Success Rate"
          value={`${successRate}%`}
          color="text-emerald-400"
          bgColor="bg-emerald-400/5"
        />
        <MetricBox
          label="Avg Duration"
          value={avgDuration ? `${avgDuration}s` : '—'}
          color="text-cyan-400"
          bgColor="bg-cyan-400/5"
        />
        <MetricBox
          label="Streak"
          value={`${streak}🔥`}
          color="text-amber-400"
          bgColor="bg-amber-400/5"
        />
      </div>

      {/* CloudWatch indicator */}
      <div className="flex items-center gap-2 mt-4 pt-3 border-t border-white/[0.04]">
        <div className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
        <span className="text-[10px] text-gray-500">
          Publishing to CloudWatch • Namespace: PULSE/Agent
        </span>
      </div>
    </div>
  );
}

function MetricBox({ label, value, color, bgColor }) {
  return (
    <div className={`p-3 rounded-xl ${bgColor} border border-white/[0.04]`}>
      <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-lg font-bold ${color}`}>{value}</p>
    </div>
  );
}
