import React from 'react';

const PHASES = [
  { id: 'observe', name: 'Observe', desc: 'Collect data' },
  { id: 'reason', name: 'Reason', desc: 'Find patterns' },
  { id: 'plan', name: 'Plan', desc: 'Set priorities' },
  { id: 'generate', name: 'Generate', desc: 'Bedrock AI' },
  { id: 'deliver', name: 'Deliver', desc: 'Email/Slack' },
  { id: 'learn', name: 'Learn', desc: 'Log metrics' },
];

export default function AgentWorkflow({ triggering }) {
  return (
    <div className="card-glass">
      <div className="flex items-center justify-between mb-3">
        <h3 className="section-title mb-0">Agent Pipeline</h3>
        {triggering && (
          <span className="text-[10px] text-emerald-400 font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Executing
          </span>
        )}
      </div>

      <div className="flex items-center gap-0.5">
        {PHASES.map((phase, idx) => (
          <React.Fragment key={phase.id}>
            <div className={`flex-1 text-center py-3 px-2 rounded-lg border transition-all ${
              triggering 
                ? 'bg-emerald-500/[0.06] border-emerald-500/20' 
                : 'bg-[#0c0f14] border-[#1e2530]'
            }`}>
              <p className={`text-[11px] font-semibold ${triggering ? 'text-emerald-300' : 'text-gray-300'}`}>
                {phase.name}
              </p>
              <p className="text-[9px] text-gray-600 mt-0.5">{phase.desc}</p>
            </div>
            {idx < PHASES.length - 1 && (
              <svg className={`w-3 h-3 flex-shrink-0 ${triggering ? 'text-emerald-500/40' : 'text-gray-700'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            )}
          </React.Fragment>
        ))}
      </div>

      <div className="flex items-center justify-between mt-3 pt-3 border-t border-[#1e2530]">
        <span className="text-[10px] text-gray-600">EventBridge → Lambda → Pipeline</span>
        <span className="text-[10px] text-gray-600">Zero human interaction</span>
      </div>
    </div>
  );
}
