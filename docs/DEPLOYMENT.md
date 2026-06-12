# Deploying Kairos (free)

Kairos deploys as **one container**: the multi-stage `Dockerfile` builds the React/Vite frontend and serves it *from* the FastAPI backend. So `/` returns the app and `/api/*` is the API — same origin, no CORS, one URL to share.

This works on any Docker host. Below: **Render** (recommended, free, no local Docker), then alternatives.

---

## What you need
- This repo on **GitHub**.
- A **free Groq API key** from [console.groq.com](https://console.groq.com) (the recommended provider). Any of Anthropic / Google / OpenAI work too — just change the env vars.

## Required environment variables (set on the host)
| Variable | Value |
|---|---|
| `LLM_PROVIDER` | `groq` |
| `GROQ_API_KEY` | *your `gsk_…` key* (mark as **secret**) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `DEMO_REFERENCE_DATE` | `2026-01-05` |

> To run with **no LLM** (deterministic mode, zero keys), set `LLM_PROVIDER=none` and skip the key.

---

## Option A — Render (recommended)

Render builds the Docker image in the cloud (you don't need Docker locally).

1. Push the repo to GitHub.
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New → Blueprint**.
3. Select your repo. Render reads **`render.yaml`** and proposes the `scholarai` web service (free plan, Docker).
4. Click **Apply**. When prompted, set **`GROQ_API_KEY`** (it's marked `sync: false` so Render won't read it from the file).
5. Wait for the build (~3–5 min). You'll get **`https://scholarai-xxxx.onrender.com`** — the full app.

**Free-tier note:** the service **sleeps after ~15 min idle** and cold-starts (~30–60 s) on the next request. Before a live demo, **open the URL once a minute beforehand** to warm it — or run locally for the live demo and use the deployed URL as the "it's live" proof.

Without the blueprint: **New → Web Service → Docker**, point at the repo root `Dockerfile`, add the env vars above manually.

---

## Option B — Hugging Face Spaces (free, Docker)

1. Create a **Space** → SDK: **Docker** → **Blank**.
2. Push the repo into the Space (it uses the root `Dockerfile`). HF expects the app on port **7860** — add `ENV PORT=7860` in the Space settings, or set the `PORT` space variable; the container already honors `$PORT`.
3. Add `GROQ_API_KEY`, `LLM_PROVIDER=groq`, etc. as **Repository secrets**.
4. The Space builds and serves the app at your `*.hf.space` URL.

## Option C — Railway / Fly.io

Both detect the root `Dockerfile`:
- **Railway:** New Project → Deploy from repo → add the env vars. (Uses trial credit.)
- **Fly.io:** `fly launch` (detects Dockerfile) → `fly secrets set GROQ_API_KEY=… LLM_PROVIDER=groq GROQ_MODEL=llama-3.3-70b-versatile` → `fly deploy`.

---

## Build & run the container locally (optional sanity check)

Requires Docker Desktop running:

```bash
docker build -t scholarai .
docker run -p 8000:8000 -e LLM_PROVIDER=groq -e GROQ_API_KEY=gsk_... -e GROQ_MODEL=llama-3.3-70b-versatile scholarai
# open http://localhost:8000
```

> On Windows, port 8000 may be reserved by Docker/Hyper-V — map a different host port, e.g. `-p 8600:8000`, then open `http://localhost:8600`.

---

## How it serves (for reference)
- `backend/app/main.py` mounts `frontend/dist` at `/` via `StaticFiles(html=True)` **after** the `/api` router, so API routes win and everything else returns the SPA.
- The frontend calls the API with the relative path `/api`, so it works identically in local dev (Vite proxy → backend) and in production (same origin).
- The container binds `0.0.0.0:$PORT`; Render/Railway/Fly inject `$PORT` automatically.

## Post-deploy checklist
- [ ] `GET /api/health` on the deployed URL returns `{"status":"ok"}`.
- [ ] The root URL loads the app; **🚀 Run Demo** completes end-to-end.
- [ ] Maya shows all three verdicts (✅ / ⚠️ / ❌) and generated documents.
- [ ] `GROQ_API_KEY` is a host **secret** — never committed (`.env` is git-ignored).
