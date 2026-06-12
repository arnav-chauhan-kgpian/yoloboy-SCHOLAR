import React, { useEffect, useState, useRef } from 'react'
import { streamSession } from '../api/client'
import NarrationStream from '../components/NarrationStream'
import EligibilityBadge from '../components/EligibilityBadge'
import ProfileSummaryCard from '../components/ProfileSummaryCard'

export default function AgentConsole({ sessionId, isDemo, onComplete }) {
  const [narration, setNarration] = useState([])
  const [state, setState] = useState(null)
  const [phase, setPhase] = useState('profile')
  const [activeNode, setActiveNode] = useState(null)
  const cleanupRef = useRef()
  const seenNarrationRef = useRef(new Set())

  useEffect(() => {
    if (!sessionId) return

    setNarration((prev) => [...prev, '🚀 Starting ScholarAI pipeline...'])

    cleanupRef.current = streamSession(
      sessionId,
      (data) => {
        if (data.node) {
          setActiveNode(data.node)
          setNarration((prev) => [
            ...prev,
            `⚙️ Running ${data.node}...`,
          ])

          if (data.output?.narration) {
            const unseen = data.output.narration.filter(
              (n) => !seenNarrationRef.current.has(n)
            )
            if (unseen.length === 0) return
            for (const n of unseen) {
              seenNarrationRef.current.add(n)
            }
            setNarration((prev) => [...prev, ...unseen])
          }
        }
        if (data.error) {
          setNarration((prev) => [...prev, `❌ Error: ${data.error}`])
        }
      },
      (err) => {
        setNarration((prev) => [...prev, `⚠️ Connection issue: ${err.message}`])
      }
    )

    return () => {
      cleanupRef.current?.()
    }
  }, [sessionId])

  useEffect(() => {
    if (!sessionId) return

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/session/${sessionId}`)
        const s = await res.json()
        setState(s)
        setPhase(s.phase || 'profile')

        // Wait for the LAST node (tracker) — guarantees documents (application_results)
        // and the action plan are already in the state before switching screens.
        if (s.tracker_result) {
          clearInterval(interval)
          setNarration((prev) => [
            ...prev,
            '✅ All agents complete! Ready for applications.',
          ])
          setTimeout(() => onComplete(s), 1500)
        }
      } catch {}
    }, 1000)

    return () => clearInterval(interval)
  }, [sessionId, onComplete])

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <h3 style={styles.sidebarTitle}>Pipeline Status</h3>
        {['profile', 'discovery', 'eligibility', 'matching', 'application', 'tracker'].map(
          (node) => (
            <div
              key={node}
              style={{
                ...styles.pipelineNode,
                backgroundColor:
                  activeNode === node
                    ? '#1e3a5f'
                    : 'transparent',
                borderLeft:
                  activeNode === node
                    ? '3px solid #38bdf8'
                    : '3px solid transparent',
              }}
            >
              <span style={styles.nodeIcon}>
                {phase === node ? '⏳' : '⬜'}
              </span>
              <span>{node.charAt(0).toUpperCase() + node.slice(1)}</span>
            </div>
          )
        )}

        {state?.profile && (
          <ProfileSummaryCard
            profile={state.profile}
            confidence={state.profile_result?.confidence}
            missingFields={state.profile_result?.missing_fields}
          />
        )}

        {state?.discovery_result && (
          <div style={styles.statsCard}>
            <h4 style={styles.statsTitle}>Discovery Results</h4>
            <p style={styles.statLine}>
              Found: {state.discovery_result.total_found} opportunities
            </p>
          </div>
        )}

        {state?.eligibility_result && (
          <div style={styles.statsCard}>
            <h4 style={styles.statsTitle}>Eligibility Screening</h4>
            <p style={{ ...styles.statLine, color: '#4ade80' }}>
              ✅ Eligible: {state.eligibility_result.eligible_count}
            </p>
            <p style={{ ...styles.statLine, color: '#facc15' }}>
              ⚠️ Borderline: {state.eligibility_result.borderline_count}
            </p>
            <p style={{ ...styles.statLine, color: '#ef4444' }}>
              ❌ Rejected: {state.eligibility_result.rejected_count}
            </p>
          </div>
        )}

        {state?.match_result?.top_picks?.length > 0 && (
          <div style={styles.statsCard}>
            <h4 style={styles.statsTitle}>Top Picks</h4>
            {state.match_result.top_picks.slice(0, 3).map((p) => (
              <div key={p.opportunity_id} style={styles.topPick}>
                <span style={{ fontSize: '12px', fontWeight: 500 }}>{p.title}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 700, color: '#38bdf8' }}>
                    {(p.match_score * 100).toFixed(0)}%
                  </span>
                  <EligibilityBadge verdict={p.eligibility_verdict} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={styles.mainArea}>
        <div style={styles.statusBar}>
          {isDemo && <span style={styles.demoBadge}>Demo Profile</span>}
          <span style={styles.statusBadge}>
            {activeNode ? `Active: ${activeNode}` : 'Waiting...'}
          </span>
          <span style={styles.phaseBadge}>Phase: {phase}</span>
        </div>

        <NarrationStream messages={narration} />

        {!state?.match_result && narration.length < 3 && (
          <div style={styles.waiting}>
            <p>Agent pipeline will start automatically after upload...</p>
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    gap: '20px',
    minHeight: '70vh',
  },
  sidebar: {
    width: '280px',
    flexShrink: 0,
  },
  sidebarTitle: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    margin: '0 0 12px',
    paddingBottom: '8px',
    borderBottom: '1px solid #334155',
  },
  pipelineNode: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 12px',
    borderRadius: '4px',
    fontSize: '13px',
    marginBottom: '4px',
  },
  nodeIcon: {
    fontSize: '14px',
    width: '20px',
  },
  statsCard: {
    backgroundColor: '#1e293b',
    borderRadius: '8px',
    border: '1px solid #334155',
    padding: '12px',
    marginTop: '16px',
  },
  statsTitle: {
    fontSize: '12px',
    fontWeight: 600,
    color: '#94a3b8',
    textTransform: 'uppercase',
    margin: '0 0 8px',
  },
  statLine: {
    fontSize: '13px',
    margin: '4px 0',
  },
  topPick: {
    backgroundColor: '#0f172a',
    borderRadius: '6px',
    padding: '8px',
    marginBottom: '6px',
  },
  mainArea: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  statusBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1e293b',
    borderRadius: '8px',
    border: '1px solid #334155',
    padding: '10px 16px',
  },
  demoBadge: {
    backgroundColor: '#2dd4bf',
    color: '#0f172a',
    padding: '4px 10px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  statusBadge: {
    backgroundColor: '#0f172a',
    color: '#38bdf8',
    padding: '4px 10px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 600,
  },
  phaseBadge: {
    backgroundColor: '#0f172a',
    color: '#94a3b8',
    padding: '4px 10px',
    borderRadius: '4px',
    fontSize: '12px',
  },
  waiting: {
    textAlign: 'center',
    color: '#64748b',
    fontSize: '14px',
    padding: '40px',
  },
}