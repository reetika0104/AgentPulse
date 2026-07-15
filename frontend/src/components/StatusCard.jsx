import React from 'react';

export default function StatusCard({ title, value, subtitle, icon, type }) {
  const getValueColor = () => {
    switch (type) {
      case 'status':
        return value === 'active' ? 'text-emerald-400' : 'text-red-400';
      case 'execution':
        return value === 'completed' ? 'text-emerald-400' :
               value === 'failed' ? 'text-red-400' : 'text-gray-300';
      case 'model':
        return 'text-purple-400';
      case 'schedule':
        return 'text-cyan-400';
      default:
        return 'text-white';
    }
  };

  const getDisplayValue = () => {
    if (type === 'status' && value === 'active') return 'Active';
    if (type === 'execution' && value === 'completed') return 'Success';
    return value;
  };

  return (
    <div className="card-glass group">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-[0.12em] mb-2">
            {title}
          </p>
          <div className="flex items-center gap-2">
            {type === 'status' && value === 'active' && (
              <span className="status-dot-active flex-shrink-0" />
            )}
            <p className={`text-base font-bold truncate ${getValueColor()}`}>
              {getDisplayValue()}
            </p>
          </div>
          {subtitle && (
            <p className="text-[10px] text-gray-600 mt-1.5 truncate">{subtitle}</p>
          )}
        </div>
        <span className="text-2xl opacity-70 group-hover:opacity-100 transition-opacity flex-shrink-0 ml-2">
          {icon}
        </span>
      </div>
    </div>
  );
}
