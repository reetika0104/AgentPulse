import React from 'react';

const PHASES = [
  { id: 'observe', name: 'Observe', description: 'Collect data' },
  { id: 'reason', name: 'Reason', description: 'Analyze patterns' },
  { id: 'plan', name: 'Plan', description: 'Prioritize' },
  { id: 'generate', name: 'Generate', description: 'Bedrock AI' },
  { id: 'deliver', name: 'Deliver', description: 'Send brief' },
  { id: 'learn', name: 'Learn', description: 'Log metrics' },
];

export default function AgentWorkflow({ triggering }) {
  return (
    <div className="card-glass">
      <div className="flex items-center justify-between mb-4">
        <h3 className="section-title mb-0">Agent Pipeline</h3>
        {triggering && (
          <span className="text-[11px] text-emerald-400 font-medium animate-pulse">
            Running
          </span>
        )}
      </div>

      <div className="flex items-center gap-1">
        {PHASES.map((phase, idx) => (
          <React.Fragment key={phase.id}>
            <div className={`flex-1 text-center py-2.5 px-1 rounded-lg transition-all duration-200 ${
              triggering ? 'bg-emerald-500/5 border border-emerald-500/20' : 'bg-[#27272a]/50'
            }`}>
              <p className={`text-[11px] font-medium ${triggering ? 'text-emerald-400' : 'text-[#a1a1aa]'}`}>
                {phase.name}
              </p>
              <p className="text-[9px] text-[#52525b] mt-0.5">
                {phase.description}
              </p>
            </div>
            {idx < PHASES.length - 1 && (
              <svg className={`w-3 h-3 flex-shrink-0 ${triggering ? 'text-emerald-500/50' : 'text-[#3f3f46]'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            )}
          </React.Fragment>
        ))}
      </div>

      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-[#27272a]">
        <span className="text-[10px] text-[#52525b]">EventBridge Scheduler → Lambda → Pipeline</span>
        <span className="text-[10px] text-[#3f3f46] ml-auto">Fully autonomous</span>
      </div>
    </div>
  );
}
