import React from 'react';

export default function BriefCard({ brief }) {
  if (!brief) {
    return (
      <div className="card-glass">
        <div className="text-center py-16">
          <h3 className="text-sm font-medium text-[#a1a1aa]">No Brief Generated Yet</h3>
          <p className="text-xs text-[#52525b] mt-2">
            Click "Run Agent" to generate your first morning brief.
          </p>
        </div>
      </div>
    );
  }

  let briefData = brief;
  if (typeof brief.content === 'string') {
    try {
      briefData = JSON.parse(brief.content);
    } catch {
      briefData = brief;
    }
  }

  const priorityScore = briefData.priority_score || brief.priority_score || 5;
  const priorityColor = priorityScore >= 8 ? 'text-red-400 border-red-500/20 bg-red-500/5' :
                         priorityScore >= 5 ? 'text-amber-400 border-amber-500/20 bg-amber-500/5' :
                         'text-emerald-400 border-emerald-500/20 bg-emerald-500/5';

  return (
    <div className="card-glass space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-sm font-semibold text-white">Today's Brief</h2>
          <p className="text-[11px] text-[#52525b] mt-0.5">
            {brief.brief_date || new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <div className={`px-3 py-1.5 rounded-lg border ${priorityColor} text-center`}>
          <p className="text-lg font-bold">{priorityScore}</p>
          <p className="text-[9px] text-[#71717a] uppercase">Score</p>
        </div>
      </div>

      {/* Greeting */}
      {briefData.greeting && (
        <p className="text-sm text-[#e4e4e7]">{briefData.greeting}</p>
      )}

      {/* Focus */}
      {briefData.suggested_focus && (
        <div className="p-3 rounded-lg bg-[#27272a]/50 border border-[#27272a]">
          <p className="text-[10px] text-[#71717a] uppercase tracking-wider mb-1">Focus</p>
          <p className="text-xs text-[#e4e4e7]">{briefData.suggested_focus}</p>
        </div>
      )}

      {/* Summary */}
      {briefData.executive_summary && (
        <p className="text-xs text-[#a1a1aa] leading-relaxed">{briefData.executive_summary}</p>
      )}

      {/* Stats */}
      <div className="grid grid-cols-4 gap-2">
        <Stat label="Meetings" value={briefData.meetings?.count || brief.meetings_today || 0} />
        <Stat label="Emails" value={briefData.emails?.unread_important || 0} />
        <Stat label="GitHub" value={briefData.github?.notifications || 0} />
        <Stat label="Urgent" value={briefData.urgent_items?.length || brief.urgent_items || 0} />
      </div>

      {/* Urgent Items */}
      {briefData.urgent_items && briefData.urgent_items.length > 0 && (
        <div className="p-3 rounded-lg border border-red-500/10 bg-red-500/[0.02]">
          <p className="text-[10px] text-red-400 uppercase tracking-wider font-medium mb-2">Urgent</p>
          <ul className="space-y-1.5">
            {briefData.urgent_items.slice(0, 4).map((item, idx) => (
              <li key={idx} className="text-xs text-[#a1a1aa] flex items-start gap-2">
                <span className="text-red-400 mt-0.5">·</span>
                <span>{typeof item === 'string' ? item : item.item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tips */}
      {briefData.productivity_tips && briefData.productivity_tips.length > 0 && (
        <div className="p-3 rounded-lg border border-[#27272a] bg-[#27272a]/30">
          <p className="text-[10px] text-[#71717a] uppercase tracking-wider font-medium mb-2">Recommendations</p>
          <ul className="space-y-1.5">
            {briefData.productivity_tips.map((tip, idx) => (
              <li key={idx} className="text-xs text-[#a1a1aa] flex items-start gap-2">
                <span className="text-[#52525b] mt-0.5">·</span>
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weather */}
      {briefData.weather && (
        <div className="flex items-center gap-2 text-xs text-[#71717a]">
          <span>{briefData.weather.summary}</span>
        </div>
      )}

      {/* Meta */}
      <div className="flex items-center justify-between text-[10px] text-[#3f3f46] pt-3 border-t border-[#27272a]">
        <span>{brief.ai_model || 'amazon.nova-micro-v1:0'}</span>
        <span>{brief.tokens_used ? `${brief.tokens_used} tokens` : ''}</span>
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="text-center p-2 rounded-lg bg-[#27272a]/50">
      <p className="text-base font-semibold text-white">{value}</p>
      <p className="text-[9px] text-[#52525b] uppercase">{label}</p>
    </div>
  );
}
