import React from 'react'

export default function MatchScore({ score }) {
  const pct = Math.round(score * 100)
  const color =
    pct >= 80 ? '#4ade80' : pct >= 60 ? '#facc15' : pct >= 40 ? '#fb923c' : '#ef4444'

  return (
    <div style={styles.wrapper} title={`Match score: ${pct}%`} aria-label={`Match score ${pct} percent`}>
      <svg width="36" height="36" viewBox="0 0 36 36">
        <title>{`Match score: ${pct}%`}</title>
        <circle
          cx="18"
          cy="18"
          r="15.5"
          fill="none"
          stroke="#1e293b"
          strokeWidth="3"
        />
        <circle
          cx="18"
          cy="18"
          r="15.5"
          fill="none"
          stroke={color}
          strokeWidth="3"
          strokeDasharray={`${2 * Math.PI * 15.5}`}
          strokeDashoffset={`${2 * Math.PI * 15.5 * (1 - score)}`}
          strokeLinecap="round"
          transform="rotate(-90, 18, 18)"
        />
        <text
          x="18"
          y="18"
          textAnchor="middle"
          dominantBaseline="central"
          fill={color}
          fontSize="9"
          fontWeight="700"
        >
          {pct}
        </text>
      </svg>
    </div>
  )
}

const styles = {
  wrapper: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
}