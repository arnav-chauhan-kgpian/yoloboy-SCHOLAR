import React from 'react'

const EMPHASIS_COLOR = '#38bdf8'

export default function ProfileSummaryCard({ profile, confidence, missingFields }) {
  const pct = Math.round((confidence || 0) * 100)
  const totalFields = 6
  const present = totalFields - (missingFields?.length || 0)
  const barPct = Math.round((present / totalFields) * 100)

  return (
    <div style={styles.card}>
      <h4 style={styles.title}>Profile Extracted</h4>

      <div style={styles.line}>
        <span style={styles.icon}>👤</span>
        <span style={styles.value}>{profile?.name || 'Unknown'}</span>
      </div>

      {profile?.major && (
        <div style={styles.line}>
          <span style={styles.icon}>🎓</span>
          <span style={styles.value}>
            {profile.major}
            {profile.degree_level ? ` — ${profile.degree_level}` : ''}
          </span>
        </div>
      )}

      {profile?.university && (
        <div style={styles.line}>
          <span style={styles.icon}>🏫</span>
          <span style={styles.value}>{profile.university}</span>
        </div>
      )}

      {profile?.gpa != null && (
        <div style={styles.line}>
          <span style={styles.icon}>📊</span>
          <span style={styles.value}>GPA {profile.gpa}</span>
        </div>
      )}

      {profile?.skills?.length > 0 && (
        <div style={styles.skillsBlock}>
          <span style={styles.skillsLabel}>Skills</span>
          <div style={styles.skillsList}>
            {profile.skills.slice(0, 5).map((s, i) => (
              <span key={i} style={styles.skillChip}>{s}</span>
            ))}
            {profile.skills.length > 5 && (
              <span style={styles.skillMore}>+{profile.skills.length - 5}</span>
            )}
          </div>
        </div>
      )}

      <div style={styles.barContainer}>
        <div style={styles.barOuter}>
          <div
            style={{
              ...styles.barInner,
              width: `${barPct}%`,
              backgroundColor: barPct >= 80 ? EMPHASIS_COLOR : barPct >= 50 ? '#facc15' : '#ef4444',
            }}
          />
        </div>
        <span style={styles.barLabel}>{pct}% confidence</span>
      </div>

      {missingFields && missingFields.length > 0 && (
        <div style={styles.warnings}>
          {missingFields.map((f) => (
            <div key={f} style={styles.warningLine}>
              ⚠️ Missing {f}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const styles = {
  card: {
    backgroundColor: '#1e293b',
    borderRadius: '8px',
    border: '1px solid #334155',
    padding: '12px',
    marginTop: '12px',
  },
  title: {
    fontSize: '12px',
    fontWeight: 600,
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    margin: '0 0 10px',
    paddingBottom: '8px',
    borderBottom: '1px solid #334155',
  },
  line: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '6px',
    marginBottom: '6px',
    fontSize: '12px',
    lineHeight: '1.4',
  },
  icon: {
    flexShrink: 0,
    fontSize: '13px',
    marginTop: '1px',
  },
  value: {
    color: '#e2e8f0',
  },
  skillsBlock: {
    marginTop: '8px',
    marginBottom: '10px',
  },
  skillsLabel: {
    fontSize: '11px',
    fontWeight: 600,
    color: '#64748b',
    textTransform: 'uppercase',
    display: 'block',
    marginBottom: '6px',
  },
  skillsList: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '4px',
  },
  skillChip: {
    backgroundColor: '#0f172a',
    color: EMPHASIS_COLOR,
    fontSize: '11px',
    padding: '2px 7px',
    borderRadius: '4px',
    fontWeight: 500,
  },
  skillMore: {
    fontSize: '11px',
    color: '#64748b',
    padding: '2px 4px',
  },
  barContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  barOuter: {
    flex: 1,
    height: '6px',
    backgroundColor: '#0f172a',
    borderRadius: '3px',
    overflow: 'hidden',
  },
  barInner: {
    height: '100%',
    borderRadius: '3px',
    transition: 'width 0.4s ease',
  },
  barLabel: {
    fontSize: '11px',
    color: '#64748b',
    whiteSpace: 'nowrap',
  },
  warnings: {
    marginTop: '8px',
    paddingTop: '8px',
    borderTop: '1px solid #334155',
  },
  warningLine: {
    fontSize: '11px',
    color: '#facc15',
    marginBottom: '2px',
  },
}