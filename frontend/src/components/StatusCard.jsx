import React from 'react';

export default function StatusCard({ title, value, subtitle, icon, type }) {
  const getValueColor = () => {
    switch (type) {
      case 'status': return value === 'active' ? 'text-emerald-400' : 'text-red-400';
      case 'execution': return value === 'completed' ? 'text-emerald-400' : value === 'failed' ? 'text-red-400' : 'text-gray-300';
      case 'schedule': return 'text-blue-400';
      case 'model': return 'text-gray-200';
      default: return 'text-white';
    }
  };

  const getDisplayValue = () => {
    if (type === 'status' && value === 'active') return 'Active';
    if (type === 'execution' && value === 'completed') return 'Success';
    return value;
  };

  return (
    <div className="card-glass">
      <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-2">{title}</p>
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            {type === 'status' && value === 'active' && <span className="status-dot-active" />}
            <p className={`text-sm font-bold ${getValueColor()}`}>{getDisplayValue()}</p>
          </div>
          {subtitle && <p className="text-[10px] text-gray-600 mt-1">{subtitle}</p>}
        </div>
        <span className="text-xl">{icon}</span>
      </div>
    </div>
  );
}
