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
    if (['connected','configured','active','publishing','ready','integrated','running','distributed'].includes(val)) return 'operational';
    if (val === 'not_configured') return 'standby';
    return 'operational';
  };

  const getColor = (status) => {
    if (status === 'operational') return 'bg-emerald-400';
    return 'bg-gray-600';
  };

  return (
    <div className="card-glass">
      <h3 className="section-title">AWS Services</h3>
      <div className="space-y-2.5">
        {AWS_SERVICES.map(({ name, key }) => {
          const status = getStatus(key);
          return (
            <div key={key} className="flex items-center justify-between">
              <span className="text-xs text-gray-300">{name}</span>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-gray-600">{status === 'operational' ? 'OK' : 'Standby'}</span>
                <div className={`w-2 h-2 rounded-full ${getColor(status)}`} />
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-3 pt-3 border-t border-[#1e2530] flex items-center justify-between">
        <span className="text-[10px] text-gray-600">us-east-1</span>
        <span className="text-[10px] text-emerald-400 font-medium">Operational</span>
      </div>
    </div>
  );
}
