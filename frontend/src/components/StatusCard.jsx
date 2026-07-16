import React from 'react';

export default function StatusCard({ title, value, subtitle, icon, type }) {
  const getValueColor = () => {
    switch (type) {
      case 'status':
        return value === 'active' ? 'text-emerald-400' : 'text-red-400';
      case 'execution':
        return value === 'completed' ? 'text-emerald-400' :
               value === 'failed' ? 'text-red-400' : 'text-[#a1a1aa]';
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
    <div className="card-glass">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-[11px] font-medium text-[#71717a] uppercase tracking-wide mb-2">
            {title}
          </p>
          <div className="flex items-center gap-2">
            {type === 'status' && value === 'active' && (
              <span className="status-dot-active flex-shrink-0" />
            )}
            <p className={`text-sm font-semibold truncate ${getValueColor()}`}>
              {getDisplayValue()}
            </p>
          </div>
          {subtitle && (
            <p className="text-[11px] text-[#52525b] mt-1.5 truncate">{subtitle}</p>
          )}
        </div>
        <span className="text-lg opacity-60 flex-shrink-0 ml-2">{icon}</span>
      </div>
    </div>
  );
}
