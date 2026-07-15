import React from 'react';

export default function ServiceHealth({ health }) {
  const services = health?.services || {};

  const getServiceStatus = (value) => {
    if (value === 'connected' || value === 'configured') return 'operational';
    if (value === 'not_configured') return 'not_configured';
    return 'degraded';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'operational': return 'bg-emerald-400';
      case 'degraded': return 'bg-amber-400';
      case 'not_configured': return 'bg-gray-600';
      default: return 'bg-red-400';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'operational': return 'Operational';
      case 'degraded': return 'Degraded';
      case 'not_configured': return 'Not Configured';
      default: return 'Down';
    }
  };

  const serviceList = [
    { name: 'Amazon Bedrock', key: 'bedrock', icon: '🧠' },
    { name: 'Database', key: 'database', icon: '💾' },
    { name: 'Amazon SES', key: 'ses', icon: '📧' },
    { name: 'Telegram', key: 'telegram', icon: '📱' },
    { name: 'Slack', key: 'slack', icon: '💬' },
  ];

  return (
    <div className="card animate-slide-up">
      <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
        Service Status
      </h3>
      <div className="space-y-3">
        {serviceList.map(({ name, key, icon }) => {
          const status = getServiceStatus(services[key]);
          return (
            <div key={key} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm">{icon}</span>
                <span className="text-sm text-gray-300">{name}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">{getStatusLabel(status)}</span>
                <span className={`w-2 h-2 rounded-full ${getStatusColor(status)}`} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Overall Status */}
      <div className="mt-4 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">Overall</span>
          <span className="text-xs text-emerald-400 font-medium">
            {health?.status === 'healthy' ? '✓ Healthy' : '⚠ Check Services'}
          </span>
        </div>
      </div>
    </div>
  );
}
