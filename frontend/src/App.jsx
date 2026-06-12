import React, { useState } from 'react'
import ProfileUpload from './screens/ProfileUpload'
import AgentConsole from './screens/AgentConsole'
import ApplicationWorkspace from './screens/ApplicationWorkspace'

const SCREENS = {
  PROFILE_UPLOAD: 'profile_upload',
  AGENT_CONSOLE: 'agent_console',
  APPLICATION_WORKSPACE: 'application_workspace',
}

export default function App() {
  const [screen, setScreen] = useState(SCREENS.PROFILE_UPLOAD)
  const [sessionId, setSessionId] = useState(null)
  const [sessionState, setSessionState] = useState(null)
  const [isDemo, setIsDemo] = useState(false)

  const handleUploadComplete = (id, demo) => {
    setSessionId(id)
    setIsDemo(!!demo)
    setScreen(SCREENS.AGENT_CONSOLE)
  }

  const handleSessionComplete = (state) => {
    setSessionState(state)
    setScreen(SCREENS.APPLICATION_WORKSPACE)
  }

  const handleNewSession = () => {
    setSessionId(null)
    setSessionState(null)
    setIsDemo(false)
    setScreen(SCREENS.PROFILE_UPLOAD)
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>ScholarAI</h1>
        <span style={styles.subtitle}>Autonomous Scholarship & Internship Agent</span>
        {isDemo && <span style={styles.demoBadge}>Demo Profile</span>}
        {sessionId && (
          <button style={styles.resetBtn} onClick={handleNewSession}>
            New Session
          </button>
        )}
      </header>
      <main style={styles.main}>
        {screen === SCREENS.PROFILE_UPLOAD && (
          <ProfileUpload onComplete={handleUploadComplete} />
        )}
        {screen === SCREENS.AGENT_CONSOLE && (
          <AgentConsole
            sessionId={sessionId}
            isDemo={isDemo}
            onComplete={handleSessionComplete}
          />
        )}
        {screen === SCREENS.APPLICATION_WORKSPACE && (
          <ApplicationWorkspace
            state={sessionState}
            onNewSession={handleNewSession}
          />
        )}
      </main>
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#0f172a',
    color: '#e2e8f0',
    fontFamily: "'Segoe UI', system-ui, sans-serif",
  },
  header: {
    backgroundColor: '#1e293b',
    borderBottom: '1px solid #334155',
    padding: '12px 24px',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  title: {
    fontSize: '20px',
    fontWeight: 700,
    color: '#38bdf8',
    margin: 0,
  },
  subtitle: {
    fontSize: '13px',
    color: '#94a3b8',
    flex: 1,
  },
  demoBadge: {
    backgroundColor: '#2dd4bf',
    color: '#0f172a',
    fontSize: '11px',
    fontWeight: 700,
    padding: '4px 10px',
    borderRadius: '4px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  resetBtn: {
    backgroundColor: '#334155',
    color: '#e2e8f0',
    border: '1px solid #475569',
    padding: '6px 14px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  main: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '24px',
  },
}