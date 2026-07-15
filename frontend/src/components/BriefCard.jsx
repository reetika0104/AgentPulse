import React from 'react';

export default function BriefCard({ brief }) {
  if (!brief) {
    return (
      <div className="card-glass">
        <div className="text-center py-16">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 mb-5">
            <svg className="w-10 h-10 text-indigo-400/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-300">No Brief Generated Yet</h3>
          <p className="text-sm text-gray-500 mt-2 max-w-sm mx-auto">
            Click "Run Agent" to trigger the autonomous pipeline.<br/>
            Or wait for the next scheduled run at 7:00 AM.
          </p>
          <div className="mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.06]">
            <span className="status-dot-active" />
            <span className="text-xs text-gray-400">Agent standing by</span>
          </div>
        </div>
      </div>
    );
  }

  // Parse brief content
  let briefData = brief;
  if (typeof brief.content === 'string') {
    try {
      briefData = JSON.parse(brief.content);
    } catch {
      briefData = brief;
    }
  }

  const priorityScore = briefData.priority_score || brief.priority_score || 5;
  const priorityColor = priorityScore >= 8 ? 'from-red-500 to-orange-500' :
                         priorityScore >= 5 ? 'from-amber-500 to-yellow-500' :
                         'from-emerald-500 to-green-500';
  const priorityBg = priorityScore >= 8 ? 'bg-red-500/10 border-red-500/20' :
                     priorityScore >= 5 ? 'bg-amber-500/10 border-amber-500/20' :
                     'bg-emerald-500/10 border-emerald-500/20';
  const priorityText = priorityScore >= 8 ? 'text-red-400' :
                       priorityScore >= 5 ? 'text-amber-400' : 'text-emerald-400';

  return (
    <div className="card-glass space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-bold text-white">Today's Intelligence Brief</h2>
          </div>
          <p className="text-xs text-gray-500">
            {brief.brief_date || new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
          </p>
        </div>

        {/* Priority Score */}
        <div className={`px-3 py-2 rounded-xl border ${priorityBg} text-center`}>
          <p className={`text-2xl font-black ${priorityText}`}>{priorityScore}</p>
          <p className="text-[9px] text-gray-500 uppercase tracking-wider">Priority</p>
        </div>
      </div>

      {/* AI Greeting */}
      {briefData.greeting && (
        <p className="text-base text-gray-200 font-medium">{briefData.greeting}</p>
      )}

      {/* Focus Area */}
      {briefData.suggested_focus && (
        <div className="flex items-center gap-3 p-3.5 rounded-xl bg-gradient-to-r from-indigo-500/5 to-purple-500/5 border border-indigo-500/15">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center flex-shrink-0">
            <span className="text-sm">🎯</span>
          </div>
          <div>
            <p className="text-[10px] text-indigo-400 uppercase tracking-wider font-medium">Suggested Focus</p>
            <p className="text-sm text-gray-200 mt-0.5">{briefData.suggested_focus}</p>
          </div>
        </div>
      )}

      {/* Executive Summary */}
      {briefData.executive_summary && (
        <p className="text-sm text-gray-400 leading-relaxed">{briefData.executive_summary}</p>
      )}

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-4 gap-2">
        <QuickStat label="Meetings" value={briefData.meetings?.count || brief.meetings_today || 0} icon="📅" color="text-blue-400" />
        <QuickStat label="Emails" value={briefData.emails?.unread_important || 0} icon="📧" color="text-purple-400" />
        <QuickStat label="GitHub" value={briefData.github?.notifications || 0} icon="🐙" color="text-gray-300" />
        <QuickStat label="Urgent" value={briefData.urgent_items?.length || brief.urgent_items || 0} icon="🚨" color="text-red-400" />
      </div>

      {/* Urgent Items */}
      {briefData.urgent_items && briefData.urgent_items.length > 0 && (
        <div className="p-4 rounded-xl bg-red-500/[0.03] border border-red-500/10">
          <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wider mb-2.5">
            🚨 Urgent Actions Required
          </h4>
          <ul className="space-y-2">
            {briefData.urgent_items.slice(0, 4).map((item, idx) => (
              <li key={idx} className="flex items-start gap-2.5">
                <div className="w-1 h-1 rounded-full bg-red-400 mt-1.5 flex-shrink-0" />
                <div>
                  <span className="text-sm text-gray-300">{typeof item === 'string' ? item : item.item}</span>
                  {item.action && <p className="text-[10px] text-gray-500 mt-0.5">→ {item.action}</p>}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Productivity Tips */}
      {briefData.productivity_tips && briefData.productivity_tips.length > 0 && (
        <div className="p-4 rounded-xl bg-emerald-500/[0.03] border border-emerald-500/10">
          <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2.5">
            💡 AI Recommendations
          </h4>
          <ul className="space-y-1.5">
            {briefData.productivity_tips.map((tip, idx) => (
              <li key={idx} className="flex items-start gap-2.5">
                <div className="w-1 h-1 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                <span className="text-sm text-gray-400">{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weather */}
      {briefData.weather && (
        <div className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/[0.04]">
          <span className="text-lg">🌤️</span>
          <div>
            <p className="text-sm text-gray-300">{briefData.weather.summary}</p>
            {briefData.weather.outfit_suggestion && (
              <p className="text-[10px] text-gray-500 mt-0.5">{briefData.weather.outfit_suggestion}</p>
            )}
          </div>
        </div>
      )}

      {/* Closing & Meta */}
      <div className="pt-4 border-t border-white/[0.04]">
        {briefData.closing_note && (
          <p className="text-center text-sm text-gray-500 italic mb-3">{briefData.closing_note}</p>
        )}
        <div className="flex items-center justify-between text-[10px] text-gray-600">
          <div className="flex items-center gap-3">
            <span>Model: {brief.ai_model || 'Amazon Nova Micro'}</span>
            <span>Tokens: {brief.tokens_used || '—'}</span>
          </div>
          <span>Confidence: 85%</span>
        </div>
      </div>
    </div>
  );
}

function QuickStat({ label, value, icon, color }) {
  return (
    <div className="text-center p-2.5 rounded-xl bg-white/[0.02] border border-white/[0.04]">
      <span className="text-sm">{icon}</span>
      <p className={`text-lg font-bold mt-0.5 ${color}`}>{value}</p>
      <p className="text-[9px] text-gray-600 uppercase tracking-wider">{label}</p>
    </div>
  );
}
