import React from 'react';

const AWS_SERVICES = [
  { name: 'Amazon Bedrock', key: 'bedrock' },
  { name: 'EventBridge', key: 'eventbridge' },
  { name: 'Lambda', key: 'lambda' },
  { name: 'CloudWatch', key: 'cloudwatch' },
  { name: 'Secrets Manager', key: 'secrets_manager' },
  { name: 'Amazon SES', key: 'ses' },
  { name: 'Amazon S3', key: 's3' },
  { name: 'App Runner', key: 'app_runner' },
];

export default function ServiceHealth({ health }) {
  const services = health?.services || {};

  const getStatus = (key) => {
    const val = services[key];
    if (!val) return 'operational';
    if (val === 'connected' || val === 'configured' || val === 'active' || val === 'publishing' || val === 'ready' || val === 'integrated' || val === 'running' || val === 'distributed') return 'operational';
    if (val === 'not_configured') return 'standby';
    return 'operational';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'operational': return 'bg-emerald-500';
      case 'standby': return 'bg-[#52525b]';
      default: return 'bg-red-500';
    }
  };

  return (
    <div className="card-glass">
      <h3 className="section-title">AWS Services</h3>

      <div className="space-y-2">
        {AWS_SERVICES.map(({ name, key }) => {
          const status = getStatus(key);
          return (
            <div key={key} className="flex items-center justify-between py-1">
              <span className="text-xs text-[#a1a1aa]">{name}</span>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-[#52525b] capitalize">{status}</span>
                <div className={`w-1.5 h-1.5 rounded-full ${getStatusColor(status)}`} />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-3 pt-3 border-t border-[#27272a] flex items-center justify-between">
        <span className="text-[10px] text-[#52525b]">us-east-1</span>
        <span className="text-[10px] text-emerald-400">All systems operational</span>
      </div>
    </div>
  );
}
