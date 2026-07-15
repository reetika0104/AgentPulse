import React from 'react';

const PHASES = [
  { id: 'observe', name: 'Observe', icon: '👁️', description: 'Collect intelligence' },
  { id: 'reason', name: 'Reason', icon: '🧠', description: 'Analyze patterns' },
  { id: 'plan', name: 'Plan', icon: '📋', description: 'Prioritize actions' },
  { id: 'generate', name: 'Generate', icon: '⚡', description: 'Bedrock Nova AI' },
  { id: 'deliver', name: 'Deliver', icon: '📬', description: 'Send via channels' },
  { id: 'learn', name: 'Learn', icon: '📊', description: 'Record metrics' },
];

export default function AgentWorkflow({ triggering }) {
  return (
    <div className="card-glass">
      <div className="flex items-center justify-between mb-4">
        <h3 className="section-title mb-0">Agent Cognitive Pipeline</h3>
        {triggering && (
          <span className="text-xs text-indigo-400 animate-pulse font-medium">
            ● Pipeline Active
          </span>
        )}
      </div>

      <div className="flex items-center justify-between gap-1 overflow-x-auto pb-2">
        {PHASES.map((phase, idx) => (
          <React.Fragment key={phase.id}>
            <div className={`flex flex-col items-center min-w-[80px] px-2 py-3 rounded-xl transition-all duration-500 ${
              triggering ? 'bg-indigo-500/5 border border-indigo-500/20' : 'bg-white/[0.02]'
            }`}>
              <span className={`text-xl mb-1.5 ${triggering ? 'animate-float' : ''}`} style={{ animationDelay: `${idx * 0.2}s` }}>
                {phase.icon}
              </span>
              <span className={`text-[11px] font-semibold ${triggering ? 'text-indigo-300' : 'text-gray-300'}`}>
                {phase.name}
              </span>
              <span className="text-[9px] text-gray-600 mt-0.5 text-center">
                {phase.description}
              </span>
            </div>
            {idx < PHASES.length - 1 && (
              <div className="flex-shrink-0">
                <svg className={`w-4 h-4 ${triggering ? 'text-indigo-400' : 'text-gray-700'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Trigger source indicator */}
      <div className="flex items-center gap-4 mt-3 pt-3 border-t border-white/[0.04]">
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-amber-400" />
          <span className="text-[10px] text-gray-500">EventBridge Scheduler → Lambda → Agent Pipeline</span>
        </div>
        <div className="flex items-center gap-1.5 ml-auto">
          <span className="text-[10px] text-gray-600">Fully autonomous • Zero interaction</span>
        </div>
      </div>
    </div>
  );
}
