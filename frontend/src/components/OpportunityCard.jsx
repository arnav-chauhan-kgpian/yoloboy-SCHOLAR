import React from 'react'
import MatchScore from './MatchScore'
import EligibilityBadge from './EligibilityBadge'

const VERDICT_COLORS = {
  eligible: '#4ade80',
  borderline: '#facc15',
  not_eligible: '#ef4444',
}

const PASS_COLOR = '#4ade80'
const FAIL_COLOR = '#ef4444'

function deadlineInfo(dateStr) {
  if (!dateStr) return null
  const now = new Date()
  const deadlineDate = new Date(dateStr)
  const diffDays = Math.ceil((deadlineDate - now) / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return { text: `Overdue by ${Math.abs(diffDays)}d`, color: '#ef4444', icon: '🚨' }
  if (diffDays === 0) return { text: 'Due today!', color: '#f97316', icon: '⏰' }
  if (diffDays <= 7) return { text: `${diffDays}d left`, color: '#f97316', icon: '🔥' }
  if (diffDays <= 30) return { text: `${diffDays}d left`, color: '#facc15', icon: '📅' }
  return { text: `${diffDays}d left`, color: '#94a3b8', icon: '📅' }
}

export default function OpportunityCard({ opportunity, eligibility }) {
  const isRejected = opportunity.eligibility_verdict === 'not_eligible'
  const isBorderline = opportunity.eligibility_verdict === 'borderline'
  const defaultOpen = isRejected || isBorderline
  const borderColor = VERDICT_COLORS[opportunity.eligibility_verdict] || '#334155'
  const dl = deadlineInfo(opportunity.deadline)

  return (
    <div style={{ ...styles.card, borderLeft: `3px solid ${borderColor}` }}>
      <div style={styles.header}>
        <div style={styles.scoreAndBadge}>
          <MatchScore score={opportunity.match_score} />
          <EligibilityBadge verdict={opportunity.eligibility_verdict} />
        </div>
        <span style={styles.type}>
          {opportunity.type === 'scholarship' ? '🎓' : '💼'}
        </span>
      </div>

      <h4 style={styles.title}>{opportunity.title}</h4>
      <p style={styles.org}>{opportunity.organization}</p>

      <div style={styles.breakdown}>
        <div style={styles.breakdownItem}>
          <span style={styles.breakdownLabel}>Academic</span>
          <span style={styles.breakdownValue}>
            {(opportunity.academic_fit * 100).toFixed(0)}%
          </span>
        </div>
        <div style={styles.breakdownItem}>
          <span style={styles.breakdownLabel}>Skills</span>
          <span style={styles.breakdownValue}>
            {(opportunity.skills_fit * 100).toFixed(0)}%
          </span>
        </div>
        <div style={styles.breakdownItem}>
          <span style={styles.breakdownLabel}>Goals</span>
          <span style={styles.breakdownValue}>
            {(opportunity.goals_fit * 100).toFixed(0)}%
          </span>
        </div>
        <div style={styles.breakdownItem}>
          <span style={styles.breakdownLabel}>Urgency</span>
          <span style={styles.breakdownValue}>
            {(opportunity.urgency * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {eligibility && eligibility.reasons && eligibility.reasons.length > 0 && (
        <details
          style={styles.details}
          open={defaultOpen}
        >
          <summary style={styles.summary}>
            <span>Eligibility Analysis</span>
            <span style={{ fontSize: '11px', color: '#64748b' }}>
              {eligibility.reasons.filter((r) => !r.passed).length} issue(s)
            </span>
          </summary>
          <div style={styles.analysisBody}>
            {eligibility.summary && (
              <p style={{
                ...styles.primaryReason,
                color: isRejected ? FAIL_COLOR : isBorderline ? '#facc15' : PASS_COLOR,
              }}>
                {eligibility.summary}
              </p>
            )}
            {eligibility.reasons.map((rule, i) => (
              <div key={i} style={styles.ruleRow}>
                <span style={styles.ruleIcon}>
                  {rule.passed ? '✅' : '❌'}
                </span>
                <div style={styles.ruleBody}>
                  <span style={{
                    ...styles.ruleName,
                    color: rule.passed ? PASS_COLOR : FAIL_COLOR,
                  }}>
                    {rule.requirement}
                  </span>
                  <div style={styles.ruleValues}>
                    <span>Profile: {rule.student_value || 'N/A'}</span>
                  </div>
                  {rule.notes && (
                    <span style={styles.ruleNote}>{rule.notes}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </details>
      )}

      {dl && (
        <p style={{ ...styles.deadline, color: dl.color }}>
          {dl.icon} {dl.text} — {opportunity.deadline}
        </p>
      )}
    </div>
  )
}

const styles = {
  card: {
    backgroundColor: '#0f172a',
    borderRadius: '8px',
    border: '1px solid #334155',
    borderLeft: '3px solid #334155',
    padding: '14px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '8px',
  },
  scoreAndBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  type: {
    fontSize: '18px',
  },
  title: {
    fontSize: '14px',
    fontWeight: 600,
    margin: '0 0 4px',
    color: '#f1f5f9',
    lineHeight: '1.3',
  },
  org: {
    fontSize: '12px',
    color: '#94a3b8',
    margin: '0 0 12px',
  },
  breakdown: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '6px',
    marginBottom: '8px',
  },
  breakdownItem: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '11px',
  },
  breakdownLabel: {
    color: '#64748b',
  },
  breakdownValue: {
    color: '#e2e8f0',
    fontWeight: 600,
  },
  details: {
    marginTop: '10px',
    marginBottom: '6px',
  },
  summary: {
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: 600,
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.3px',
    padding: '6px 0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    userSelect: 'none',
  },
  analysisBody: {
    backgroundColor: '#020617',
    borderRadius: '6px',
    padding: '10px 12px',
    marginTop: '4px',
  },
  primaryReason: {
    fontSize: '12px',
    fontWeight: 500,
    margin: '0 0 10px',
    lineHeight: '1.5',
    padding: '6px 8px',
    backgroundColor: '#0f172a',
    borderRadius: '4px',
  },
  ruleRow: {
    display: 'flex',
    gap: '8px',
    padding: '6px 0',
    borderBottom: '1px solid #1e293b',
  },
  ruleIcon: {
    fontSize: '13px',
    flexShrink: 0,
    marginTop: '1px',
  },
  ruleBody: {
    flex: 1,
    minWidth: 0,
  },
  ruleName: {
    fontSize: '12px',
    fontWeight: 600,
    display: 'block',
    marginBottom: '2px',
  },
  ruleValues: {
    display: 'flex',
    gap: '12px',
    fontSize: '11px',
    color: '#94a3b8',
  },
  ruleNote: {
    fontSize: '11px',
    color: '#64748b',
    marginTop: '2px',
    display: 'block',
    fontStyle: 'italic',
  },
  deadline: {
    fontSize: '11px',
    color: '#94a3b8',
    margin: '4px 0 0',
  },
}