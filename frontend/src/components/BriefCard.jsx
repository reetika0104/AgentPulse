import React from 'react';

export default function BriefCard({ brief }) {
  if (!brief) {
    return (
      <div className="card-glass">
        <div className="text-center py-14">
          <p className="text-sm text-gray-400">No brief generated yet</p>
          <p className="text-xs text-gray-600 mt-1">Click "Run Agent" to trigger the pipeline</p>
        </div>
      </div>
    );
  }

  let briefData = brief;
  if (typeof brief.content === 'string') {
    try { briefData = JSON.parse(brief.content); } catch { briefData = brief; }
  }

  const priorityScore = briefData.priority_score || brief.priority_score || 5;
  const scoreColor = priorityScore >= 8 ? 'text-red-400 border-red-500/30 bg-red-500/10' :
                     priorityScore >= 5 ? 'text-amber-400 border-amber-500/30 bg-amber-500/10' :
                     'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';

  return (
    <div className="card-glass space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-base font-bold text-white">Morning Brief</h2>
          <p className="text-[11px] text-gray-500 mt-0.5">
            {brief.brief_date || new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
          </p>
        </div>
        <div className={`w-12 h-12 rounded-xl border flex flex-col items-center justify-center ${scoreColor}`}>
          <span className="text-xl font-black leading-none">{priorityScore}</span>
          <span className="text-[8px] opacity-70 mt-0.5">/ 10</span>
        </div>
      </div>

      {/* Greeting */}
      {briefData.greeting && (
        <p className="text-sm text-gray-200">{briefData.greeting}</p>
      )}

      {/* Focus */}
      {briefData.suggested_focus && (
        <div className="p-3 rounded-lg bg-blue-500/[0.04] border border-blue-500/10">
          <p className="text-[9px] text-blue-400/80 uppercase tracking-wider font-semibold mb-1">Today's Focus</p>
          <p className="text-xs text-gray-300">{briefData.suggested_focus}</p>
        </div>
      )}

      {/* Summary */}
      {briefData.executive_summary && (
        <p className="text-xs text-gray-400 leading-relaxed">{briefData.executive_summary}</p>
      )}

      {/* Stats */}
      <div className="grid grid-cols-4 gap-2">
        <div className="stat-card">
          <p className="text-lg font-bold text-white">{briefData.meetings?.count || brief.meetings_today || 0}</p>
          <p className="text-[9px] text-gray-500 uppercase mt-0.5">Meetings</p>
        </div>
        <div className="stat-card">
          <p className="text-lg font-bold text-white">{briefData.emails?.unread_important || 0}</p>
          <p className="text-[9px] text-gray-500 uppercase mt-0.5">Emails</p>
        </div>
        <div className="stat-card">
          <p className="text-lg font-bold text-white">{briefData.github?.notifications || 0}</p>
          <p className="text-[9px] text-gray-500 uppercase mt-0.5">GitHub</p>
        </div>
        <div className="stat-card">
          <p className="text-lg font-bold text-white">{briefData.urgent_items?.length || brief.urgent_items || 0}</p>
          <p className="text-[9px] text-gray-500 uppercase mt-0.5">Urgent</p>
        </div>
      </div>

      {/* Urgent Items */}
      {briefData.urgent_items && briefData.urgent_items.length > 0 && (
        <div className="p-3 rounded-lg bg-red-500/[0.03] border border-red-500/10">
          <p className="text-[9px] text-red-400 uppercase tracking-wider font-semibold mb-2">Urgent Actions</p>
          <ul className="space-y-2">
            {briefData.urgent_items.slice(0, 4).map((item, idx) => (
              <li key={idx} className="text-xs text-gray-300">
                <span className="font-medium">{typeof item === 'string' ? item : item.item}</span>
                {item.action && <p className="text-gray-500 text-[11px] mt-0.5">→ {item.action}</p>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tips */}
      {briefData.productivity_tips && briefData.productivity_tips.length > 0 && (
        <div className="p-3 rounded-lg bg-[#0c0f14] border border-[#1e2530]">
          <p className="text-[9px] text-gray-500 uppercase tracking-wider font-semibold mb-2">AI Recommendations</p>
          <ul className="space-y-1.5">
            {briefData.productivity_tips.map((tip, idx) => (
              <li key={idx} className="text-xs text-gray-400 pl-3 relative before:content-[''] before:absolute before:left-0 before:top-[7px] before:w-1 before:h-1 before:rounded-full before:bg-gray-600">
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weather */}
      {briefData.weather && (
        <p className="text-xs text-gray-500">{briefData.weather.summary}{briefData.weather.outfit_suggestion ? ` — ${briefData.weather.outfit_suggestion}` : ''}</p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-[10px] text-gray-600 pt-3 border-t border-[#1e2530]">
        <span>{brief.ai_model || 'amazon.nova-micro-v1:0'}</span>
        <span>{brief.tokens_used ? `${brief.tokens_used} tokens` : ''}</span>
      </div>
    </div>
  );
}
