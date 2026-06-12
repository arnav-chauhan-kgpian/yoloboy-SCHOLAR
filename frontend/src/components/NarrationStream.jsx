import React, { useEffect, useRef } from 'react'

export default function NarrationStream({ messages }) {
  const bottomRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>🧠 Kairos · Live Reasoning</h3>
      <div style={styles.stream}>
        {messages.map((msg, i) => {
          const isAgent = msg.includes(']')
          const isError = msg.includes('Error') || msg.includes('❌')
          const isComplete = msg.includes('✅')
          return (
            <div
              key={i}
              style={{
                ...styles.message,
                color: isError
                  ? '#ef4444'
                  : isComplete
                  ? '#4ade80'
                  : '#e2e8f0',
                fontWeight: isAgent ? 400 : 300,
              }}
            >
              {msg}
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}

const styles = {
  container: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#1e293b',
    borderRadius: '8px',
    border: '1px solid #334155',
    overflow: 'hidden',
  },
  title: {
    fontSize: '12px',
    fontWeight: 600,
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    padding: '8px 16px',
    margin: 0,
    borderBottom: '1px solid #334155',
  },
  stream: {
    flex: 1,
    padding: '12px 16px',
    overflowY: 'auto',
    maxHeight: '500px',
    fontFamily: "'Cascadia Code', 'Fira Code', monospace",
    fontSize: '13px',
    lineHeight: '1.7',
  },
  message: {
    padding: '2px 0',
  },
}