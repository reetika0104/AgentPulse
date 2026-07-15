import React from 'react';

export default function BriefCard({ brief }) {
  if (!brief) {
    return (
      <div className="card animate-fade-in">
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-800 mb-4">
            <svg className="w-8 h-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-400">No Brief Yet</h3>
          <p className="text-gray-500 text-sm mt-1">
            Click "Run Now" to generate your first morning brief
          </p>
        </div>
      </div>
    );
  }

  // Parse brief content if it's a string
  let briefData = brief;
  if (typeof brief.content === 'string') {
    try {
      briefData = JSON.parse(brief.content);
    } catch {
      briefData = brief;
    }
  }

  const priorityScore = briefData.priority_score || brief.priority_score || 5;
  const priorityColor = priorityScore >= 8 ? 'text-red-400 bg-red-400/10' :
                         priorityScore >= 5 ? 'text-amber-400 bg-amber-400/10' :
                         'text-emerald-400 bg-emerald-400/10';

  return (
    <div className="card animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            ⚡ Today's Brief
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            {brief.brief_date || new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <div className={`px-3 py-1.5 rounded-lg font-bold text-lg ${priorityColor}`}>
          {priorityScore}/10
        </div>
      </div>

      {/* Greeting & Summary */}
      {briefData.greeting && (
        <p className="text-gray-300 text-lg">{briefData.greeting}</p>
      )}

      {briefData.suggested_focus && (
        <div className="flex items-center gap-3 p-3 bg-pulse-600/10 border border-pulse-600/20 rounded-lg">
          <span className="text-lg">🎯</span>
          <p className="text-pulse-300 font-medium">{briefData.suggested_focus}</p>
        </div>
      )}

      {briefData.executive_summary && (
        <p className="text-gray-400 leading-relaxed">{briefData.executive_summary}</p>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MiniStat label="Meetings" value={briefData.meetings?.count || brief.meetings_today || 0} icon="📅" />
        <MiniStat label="Emails" value={briefData.emails?.unread_important || 0} icon="📧" />
        <MiniStat label="GitHub" value={briefData.github?.notifications || 0} icon="🐙" />
        <MiniStat label="Urgent" value={briefData.urgent_items?.length || brief.urgent_items || 0} icon="🚨" />
      </div>

      {/* Urgent Items */}
      {briefData.urgent_items && briefData.urgent_items.length > 0 && (
        <div className="p-4 bg-red-500/5 border border-red-500/20 rounded-lg">
          <h3 className="text-sm font-medium text-red-400 mb-2">🚨 Urgent Items</h3>
          <ul className="space-y-2">
            {briefData.urgent_items.slice(0, 5).map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                <span className="text-red-400 mt-0.5">•</span>
                <span>{typeof item === 'string' ? item : item.item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Productivity Tips */}
      {briefData.productivity_tips && briefData.productivity_tips.length > 0 && (
        <div className="p-4 bg-emerald-500/5 border border-emerald-500/20 rounded-lg">
          <h3 className="text-sm font-medium text-emerald-400 mb-2">💡 Productivity Tips</h3>
          <ul className="space-y-1.5">
            {briefData.productivity_tips.map((tip, idx) => (
              <li key={idx} className="text-sm text-gray-400 flex items-start gap-2">
                <span className="text-emerald-400 mt-0.5">•</span>
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weather */}
      {briefData.weather && (
        <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
          <span className="text-lg">🌤️</span>
          <div>
            <p className="text-sm text-gray-300">{briefData.weather.summary}</p>
            {briefData.weather.outfit_suggestion && (
              <p className="text-xs text-gray-500 mt-0.5">{briefData.weather.outfit_suggestion}</p>
            )}
          </div>
        </div>
      )}

      {/* Closing */}
      {briefData.closing_note && (
        <p className="text-center text-sm text-gray-500 italic pt-2 border-t border-gray-800">
          {briefData.closing_note}
        </p>
      )}

      {/* Meta */}
      <div className="flex items-center justify-between text-xs text-gray-600 pt-2">
        <span>Model: {brief.ai_model || 'Amazon Nova'}</span>
        <span>Tokens: {brief.tokens_used || 'N/A'}</span>
      </div>
    </div>
  );
}

function MiniStat({ label, value, icon }) {
  return (
    <div className="p-3 bg-gray-800/50 rounded-lg text-center">
      <span className="text-lg">{icon}</span>
      <p className="text-xl font-bold text-white mt-1">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}
