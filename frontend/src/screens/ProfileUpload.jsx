import React, { useState, useRef } from 'react'
import { uploadResume, startDemo } from '../api/client'

export default function ProfileUpload({ onComplete }) {
  const [loading, setLoading] = useState(false)
  const [demoLoading, setDemoLoading] = useState(false)
  const [error, setError] = useState(null)
  const [file, setFile] = useState(null)
  const fileRef = useRef()

  const handleDrop = (e) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f && (f.name.endsWith('.pdf') || f.name.endsWith('.docx') || f.name.endsWith('.txt'))) {
      setFile(f)
      setError(null)
    } else {
      setError('Please upload a PDF, DOCX, or TXT file')
    }
  }

  const handleSubmit = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const result = await uploadResume(file)
      onComplete(result.session_id, false)
    } catch (err) {
      setError('Upload failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDemo = async () => {
    setDemoLoading(true)
    setError(null)
    try {
      const result = await startDemo()
      onComplete(result.session_id, true)
    } catch (err) {
      setError('Demo failed to start. Please try again.')
    } finally {
      setDemoLoading(false)
    }
  }

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <h2 style={styles.heading}>Upload Your Resume</h2>
        <p style={styles.description}>
          I'll scan your resume, extract your profile, and autonomously discover matching scholarships and internships.
        </p>

        <div
          style={styles.dropzone}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => fileRef.current?.click()}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx,.txt"
            style={{ display: 'none' }}
            onChange={(e) => {
              const f = e.target.files[0]
              if (f) { setFile(f); setError(null) }
            }}
          />
          {file ? (
            <p style={styles.fileName}>{file.name}</p>
          ) : (
            <p style={styles.dropText}>Drop your resume here or click to browse</p>
          )}
        </div>

        {error && <p style={styles.error}>{error}</p>}

        <button
          style={{ ...styles.button, opacity: file ? 1 : 0.5 }}
          disabled={!file || loading}
          onClick={handleSubmit}
        >
          {loading ? 'Processing...' : 'Start Analysis'}
        </button>

        <div style={styles.divider}>
          <span style={styles.dividerLine} />
          <span style={styles.dividerText}>or</span>
          <span style={styles.dividerLine} />
        </div>

        <button
          style={styles.demoButton}
          disabled={demoLoading}
          onClick={handleDemo}
        >
          {demoLoading ? 'Starting...' : '🚀 Run Demo'}
        </button>
        <p style={styles.demoHint}>
          Uses a sample student profile. No upload needed.
        </p>
      </div>
    </div>
  )
}

const styles = {
  wrapper: {
    display: 'flex',
    justifyContent: 'center',
    paddingTop: '60px',
  },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: '12px',
    border: '1px solid #334155',
    padding: '40px',
    width: '100%',
    maxWidth: '480px',
  },
  heading: {
    fontSize: '24px',
    fontWeight: 600,
    margin: '0 0 8px',
    color: '#f1f5f9',
  },
  description: {
    fontSize: '14px',
    color: '#94a3b8',
    margin: '0 0 24px',
    lineHeight: '1.5',
  },
  dropzone: {
    border: '2px dashed #475569',
    borderRadius: '8px',
    padding: '40px 20px',
    textAlign: 'center',
    cursor: 'pointer',
    marginBottom: '20px',
    transition: 'border-color 0.2s',
  },
  dropText: {
    color: '#64748b',
    margin: 0,
    fontSize: '14px',
  },
  fileName: {
    color: '#38bdf8',
    margin: 0,
    fontSize: '14px',
    fontWeight: 500,
  },
  error: {
    color: '#ef4444',
    fontSize: '13px',
    margin: '0 0 12px',
  },
  button: {
    width: '100%',
    backgroundColor: '#38bdf8',
    color: '#0f172a',
    border: 'none',
    padding: '12px',
    borderRadius: '8px',
    fontSize: '15px',
    fontWeight: 600,
    cursor: 'pointer',
  },
  divider: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    margin: '20px 0',
  },
  dividerLine: {
    flex: 1,
    height: '1px',
    backgroundColor: '#334155',
  },
  dividerText: {
    color: '#64748b',
    fontSize: '12px',
    textTransform: 'uppercase',
  },
  demoButton: {
    width: '100%',
    backgroundColor: '#2dd4bf',
    color: '#0f172a',
    border: 'none',
    padding: '14px',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 700,
    cursor: 'pointer',
  },
  demoHint: {
    textAlign: 'center',
    color: '#64748b',
    fontSize: '12px',
    margin: '8px 0 0',
  },
}