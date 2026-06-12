import React from 'react'
import OpportunityCard from '../components/OpportunityCard'

export default function ApplicationWorkspace({ state, onNewSession }) {
  if (!state) {
    return (
      <div style={{ textAlign: 'center', padding: '60px' }}>
        <p>No session data available. Start a new session.</p>
        <button onClick={onNewSession} style={styles.button}>
          Start New Session
        </button>
      </div>
    )
  }

  const matchResult = state.match_result
  const eligibilityResult = state.eligibility_result
  const eligibilityMap = Object.fromEntries(
    (eligibilityResult?.results || []).map((r) => [r.opportunity_id, r])
  )
  const trackerResult = state.tracker_result
  const applicationResults = state.application_results || []

  const groupByVerdict = (opps) => {
    const groups = { eligible: [], borderline: [], not_eligible: [] }
    for (const o of opps) {
      const key = o.eligibility_verdict || 'not_eligible'
      if (groups[key]) groups[key].push(o)
    }
    return groups
  }

  const grouped = matchResult ? groupByVerdict(matchResult.ranked_opportunities || []) : {}
  const VERDICT_SECTIONS = [
    { key: 'eligible', label: '✅ Eligible', color: '#4ade80' },
    { key: 'borderline', label: '⚠️ Borderline', color: '#facc15' },
    { key: 'not_eligible', label: '❌ Not Eligible', color: '#ef4444' },
  ]

  return (
    <div style={styles.container}>
      <div style={styles.summaryBar}>
        <h2 style={styles.heading}>Application Workspace</h2>
        <button onClick={onNewSession} style={styles.button}>
          New Session
        </button>
      </div>

      {matchResult && (
        <section style={styles.section}>
          <h3 style={styles.sectionTitle}>
            🏆 All Opportunities ({(matchResult.ranked_opportunities || []).length})
          </h3>
          {VERDICT_SECTIONS.map(({ key, label, color }) => {
            const items = grouped[key] || []
            if (items.length === 0) return null
            return (
              <div key={key} style={{ marginBottom: '16px' }}>
                <h4 style={{ ...styles.groupHeader, color }}>
                  {label}
                  <span style={styles.groupCount}>{items.length}</span>
                </h4>
                <div style={styles.cardsGrid}>
                  {items.slice(0, 10).map((opp) => (
                    <OpportunityCard
                      key={opp.opportunity_id}
                      opportunity={opp}
                      eligibility={eligibilityMap[opp.opportunity_id] || null}
                    />
                  ))}
                </div>
              </div>
            )
          })}
        </section>
      )}

      {trackerResult && (
        <section style={styles.section}>
          <h3 style={styles.sectionTitle}>📅 Action Plan</h3>
          <div style={styles.trackerGrid}>
            <div style={styles.trackerColumn}>
              <h4 style={{ ...styles.columnHeader, color: '#ef4444' }}>
                🚨 Immediate ({trackerResult.action_plan.immediate.length})
              </h4>
              {trackerResult.action_plan.immediate.map((e) => (
                <div key={e.opportunity_id} style={styles.trackerCard}>
                  <p style={{ fontWeight: 500, margin: '0 0 4px', color: '#f1f5f9' }}>{e.title}</p>
                  <p style={{
                    fontSize: '12px',
                    margin: 0,
                    color: e.days_remaining < 0 ? '#ef4444' : e.days_remaining <= 3 ? '#f97316' : '#facc15',
                    fontWeight: 600,
                  }}>
                    {e.days_remaining < 0 ? `🚨 OVERDUE by ${Math.abs(e.days_remaining)} days` :
                     e.days_remaining === 0 ? '⏰ Due today!' :
                     e.days_remaining <= 3 ? `🔥 ${e.days_remaining} day${e.days_remaining > 1 ? 's' : ''} left` :
                     `📅 ${e.days_remaining} days remaining`}
                  </p>
                </div>
              ))}
            </div>
            <div style={styles.trackerColumn}>
              <h4 style={{ ...styles.columnHeader, color: '#facc15' }}>
                📋 Upcoming ({trackerResult.action_plan.upcoming.length})
              </h4>
              {trackerResult.action_plan.upcoming.map((e) => (
                <div key={e.opportunity_id} style={styles.trackerCard}>
                  <p style={{ fontWeight: 500, margin: '0 0 4px', color: '#f1f5f9' }}>{e.title}</p>
                  <p style={{ fontSize: '12px', margin: 0, color: '#facc15' }}>
                    {e.days_remaining !== null && e.days_remaining !== undefined
                      ? `📅 ${e.days_remaining} day${e.days_remaining !== 1 ? 's' : ''} until deadline`
                      : 'No deadline'}
                  </p>
                </div>
              ))}
            </div>
            <div style={styles.trackerColumn}>
              <h4 style={{ ...styles.columnHeader, color: '#64748b' }}>
                👀 Watchlist ({trackerResult.action_plan.watchlist.length})
              </h4>
              {trackerResult.action_plan.watchlist.map((e) => (
                <div key={e.opportunity_id} style={styles.trackerCard}>
                  <p style={{ fontWeight: 500, margin: '0 0 4px', color: '#94a3b8' }}>{e.title}</p>
                  {e.days_remaining !== null && e.days_remaining !== undefined && (
                    <p style={{ fontSize: '11px', margin: 0, color: '#64748b' }}>
                      📅 {e.days_remaining} day{e.days_remaining !== 1 ? 's' : ''} remaining
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <section style={styles.section}>
        <h3 style={styles.sectionTitle}>📄 Generated Documents</h3>
        {applicationResults.length === 0 ? (
          <p style={{ color: '#64748b' }}>No documents generated yet.</p>
        ) : (
          applicationResults.map((app) => (
            <div key={app.opportunity_id} style={styles.docGroup}>
              <h4 style={{ color: '#38bdf8', margin: '0 0 8px' }}>{app.opportunity_title}</h4>
              <div style={styles.docList}>
                {app.documents.map((doc, i) => (
                  <details key={i} style={styles.docDetails}>
                    <summary style={styles.docSummary}>
                      {doc.type === 'resume' && '📄 '}
                      {doc.type === 'cover_letter' && '✉️ '}
                      {doc.type === 'sop' && '📝 '}
                      {doc.type.toUpperCase().replace('_', ' ')}
                    </summary>
                    <pre style={styles.docContent}>{doc.content}</pre>
                  </details>
                ))}
              </div>
            </div>
          ))
        )}
      </section>
    </div>
  )
}

const styles = {
  container: {},
  summaryBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  heading: {
    fontSize: '22px',
    fontWeight: 600,
    margin: 0,
    color: '#f1f5f9',
  },
  button: {
    backgroundColor: '#334155',
    color: '#e2e8f0',
    border: '1px solid #475569',
    padding: '8px 16px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  section: {
    backgroundColor: '#1e293b',
    borderRadius: '12px',
    border: '1px solid #334155',
    padding: '20px',
    marginBottom: '20px',
  },
  sectionTitle: {
    fontSize: '16px',
    fontWeight: 600,
    margin: '0 0 16px',
    color: '#e2e8f0',
  },
  groupHeader: {
    fontSize: '13px',
    fontWeight: 600,
    margin: '0 0 8px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  groupCount: {
    fontSize: '11px',
    color: '#64748b',
    fontWeight: 400,
  },
  cardsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '12px',
  },
  trackerGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '12px',
  },
  trackerColumn: {},
  columnHeader: {
    fontSize: '13px',
    fontWeight: 600,
    margin: '0 0 8px',
    textTransform: 'uppercase',
    letterSpacing: '0.3px',
  },
  trackerCard: {
    backgroundColor: '#0f172a',
    borderRadius: '6px',
    border: '1px solid #334155',
    padding: '10px',
    marginBottom: '6px',
  },
  docGroup: {
    marginBottom: '16px',
  },
  docList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  docDetails: {
    backgroundColor: '#0f172a',
    borderRadius: '6px',
    border: '1px solid #334155',
    padding: '8px 12px',
  },
  docSummary: {
    cursor: 'pointer',
    fontWeight: 500,
    fontSize: '13px',
    color: '#e2e8f0',
  },
  docContent: {
    whiteSpace: 'pre-wrap',
    fontSize: '12px',
    color: '#94a3b8',
    marginTop: '8px',
    padding: '8px',
    backgroundColor: '#020617',
    borderRadius: '4px',
    maxHeight: '300px',
    overflowY: 'auto',
  },
}