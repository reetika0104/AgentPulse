import React from 'react';

export default function MetricsPanel({ metrics, executions }) {
  const totalRuns = metrics?.total_runs || executions?.length || 0;
  const successRate = metrics?.success_rate || (totalRuns > 0 ? 100 : 0);
  const avgDuration = metrics?.avg_duration_seconds || 0;
  const streak = metrics?.streak || 0;

  return (
    <div className="card-glass">
      <h3 className="section-title">Performance</h3>
      <div className="grid grid-cols-2 gap-2">
        <div className="stat-card">
          <p className="text-[9px] text-gray-500 uppercase mb-1">Runs</p>
          <p className="text-xl font-bold text-white">{totalRuns}</p>
        </div>
        <div className="stat-card">
          <p className="text-[9px] text-gray-500 uppercase mb-1">Success</p>
          <p className="text-xl font-bold text-emerald-400">{successRate}%</p>
        </div>
        <div className="stat-card">
          <p className="text-[9px] text-gray-500 uppercase mb-1">Avg Time</p>
          <p className="text-xl font-bold text-white">{avgDuration ? `${avgDuration}s` : '—'}</p>
        </div>
        <div className="stat-card">
          <p className="text-[9px] text-gray-500 uppercase mb-1">Streak</p>
          <p className="text-xl font-bold text-white">{streak}</p>
        </div>
      </div>
      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-[#1e2530]">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        <span className="text-[10px] text-gray-600">Publishing to CloudWatch</span>
      </div>
    </div>
  );
}
