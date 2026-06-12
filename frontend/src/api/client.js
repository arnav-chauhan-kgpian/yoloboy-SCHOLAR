const API_BASE = '/api'

export async function uploadResume(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_BASE}/upload-resume`, { method: 'POST', body: form })
  return res.json()
}

export async function startDemo() {
  const res = await fetch(`${API_BASE}/demo`, { method: 'POST' })
  return res.json()
}

export function streamSession(sessionId, onData, onError) {
  const evtSource = new EventSource(`${API_BASE}/start-session/${sessionId}`)

  evtSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onData(data)
    } catch (e) {
      onError?.(e)
    }
  }

  evtSource.onerror = (err) => {
    onError?.(err)
    evtSource.close()
  }

  return () => evtSource.close()
}

export async function getSession(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}`)
  return res.json()
}

export const API_BASE_URL = API_BASE