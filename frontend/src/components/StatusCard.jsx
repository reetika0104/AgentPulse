import React from 'react';

export default function StatusCard({ title, value, icon, type }) {
  const getStatusColor = () => {
    switch (type) {
      case 'status':
        return value === 'active' ? 'text-emerald-400' : 'text-red-400';
      case 'execution':
        return value === 'completed' ? 'text-emerald-400' : value === 'failed' ? 'text-red-400' : 'text-gray-400';
      default:
        return 'text-pulse-400';
    }
  };

  const getStatusDot = () => {
    if (type === 'status' && value === 'active') {
      return <span className="status-dot-active" />;
    }
    return null;
  };

  return (
    <div className="card-glow animate-slide-up">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">{title}</p>
          <div className="flex items-center gap-2 mt-1">
            {getStatusDot()}
            <p className={`text-lg font-semibold ${getStatusColor()}`}>
              {value === 'active' ? 'Active' : value}
            </p>
          </div>
        </div>
        <span className="text-2xl">{icon}</span>
      </div>
    </div>
  );
}
