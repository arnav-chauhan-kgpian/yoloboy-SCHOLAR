import React from 'react'

const BADGE_STYLES = {
  eligible: { bg: '#052e16', text: '#4ade80', label: '✅ Eligible' },
  borderline: { bg: '#422006', text: '#facc15', label: '⚠️ Borderline' },
  not_eligible: { bg: '#450a0a', text: '#ef4444', label: '❌ Not Eligible' },
}

export default function EligibilityBadge({ verdict }) {
  const style = BADGE_STYLES[verdict] || BADGE_STYLES.not_eligible

  return (
    <span
      style={{
        backgroundColor: style.bg,
        color: style.text,
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '11px',
        fontWeight: 600,
        whiteSpace: 'nowrap',
      }}
    >
      {style.label}
    </span>
  )
}