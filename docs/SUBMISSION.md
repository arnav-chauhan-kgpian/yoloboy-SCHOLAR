# Kairos — Submission Pack

Everything needed for the hackathon submission form, judging, and the live demo.

---

## 1. Submission Descriptions

### Short (50 words)
Kairos is an autonomous multi-agent system that turns a single résumé into funded opportunities. It finds scholarships and internships, checks eligibility with exact, explainable reasoning (✅/⚠️/❌), ranks the best matches, and drafts tailored applications — running live end-to-end, even with no API key.

### Medium (150 words)
Every year, billions in scholarships go unclaimed — not because students don't qualify, but because checking eligibility across hundreds of programs and tailoring each application takes hours.

Kairos is an autonomous multi-agent system that fixes this. A student uploads their résumé once; Kairos then extracts their profile, discovers relevant scholarships and internships, and screens each one with an **explainable eligibility engine** that says exactly why an opportunity is Eligible, Borderline, or Not Eligible (e.g., *"Requires US Citizenship. Student = International Student"*). It then ranks the strongest matches by fit and urgency, generates tailored résumés, cover letters, and statements of purpose, and builds a deadline-aware action plan.

Built on LangGraph as a blackboard multi-agent pipeline, Kairos narrates its reasoning live and runs fully end-to-end **even with no API key**, thanks to a deterministic fallback mode — making the demo bulletproof and the verdicts reproducible.

### Long (400–500 words)
**The problem.** Every year, billions of dollars in scholarships and internships go unclaimed. The reason isn't a lack of qualified students — it's friction. Opportunities are scattered across hundreds of sources, each with eligibility rules buried in fine print: citizenship, GPA floors, field of study, degree level, deadlines. Verifying eligibility is tedious and error-prone, and every application demands a freshly tailored résumé, cover letter, and statement of purpose. A single quality application takes 3–6 hours, so the students who need help most — first-generation, low-income, and international applicants — are the ones most likely to give up.

**The solution.** Kairos is an autonomous multi-agent system that compresses a week of work into a few minutes. A student uploads their résumé once, and Kairos takes over:

1. A **Profile Agent** extracts a structured profile (skills, GPA, field, level, citizenship, goals).
2. A **Discovery Agent** assembles relevant scholarships and internships from a curated library of 101 opportunities.
3. An **Eligibility Agent** — the heart of the product — screens each opportunity rule-by-rule and explains *exactly why* it's ✅ Eligible, ⚠️ Borderline, or ❌ Not Eligible, e.g. *"Requires US Citizenship. Student = International Student"* or *"GPA 3.7 is just under the 3.8 requirement."*
4. A **Match Agent** ranks the best options with a transparent score (Academic / Skills / Goals / Urgency).
5. An **Application Agent** drafts tailored résumés, cover letters, and SOPs.
6. A **Tracker Agent** builds a prioritized, deadline-aware action plan.

**Why it's a real agent.** Kairos is a blackboard multi-agent system orchestrated by LangGraph: each agent reads and writes a shared state, the graph sequences the work, and the whole loop runs autonomously from a single trigger while narrating its reasoning live. It doesn't answer questions — it *does the work*: filtering, deciding, prioritizing, and producing artifacts a student can actually submit.

**Why it's trustworthy.** The parts judges scrutinize most — eligibility verdicts and match scores — are **deterministic and rule-based**, not LLM guesses. The LLM is used for extraction and writing; verdicts are reproducible. And because every agent has a deterministic fallback, Kairos runs fully end-to-end **with no API key at all** — the demo can't hang on a network call or show an empty board.

**Impact.** Kairos turns "I qualify but it's too much work" into "here are the three I should apply to first, and here are my drafts." For students like our demo persona Maya — an international, first-generation, pre-med undergraduate — that's the difference between giving up and getting funded.

---

## 2. Judge Q&A Preparation

**1. Why is this an AI Agent?**
It's an autonomous multi-agent system, not a single prompt. Six specialized agents (Profile, Discovery, Eligibility, Match, Application, Tracker) are orchestrated by a LangGraph state machine over a shared `SessionState`. From one trigger, the system independently sequences multiple steps — extracting, searching, reasoning, deciding, prioritizing, and producing artifacts — and narrates that work live. The agents take actions and make decisions on the student's behalf; they don't just respond to a chat turn.

**2. Why not just a chatbot?**
A chatbot answers questions. Kairos *does the work*: it filters hundreds of criteria, renders eligibility verdicts with reasons, ranks by fit and urgency, generates documents, and schedules deadlines — autonomously, in one pass. There's no back-and-forth required; the output is a decision-ready board and ready-to-edit drafts, not a conversation.

**3. How does eligibility work?**
Deterministically, in two layers. Each opportunity's criteria are checked rule-by-rule (citizenship, GPA, degree level, field) against the profile. Each failing rule is tagged `hard` (disqualifying) or `soft` (near-miss). A fixed rollup decides the verdict: any hard fail → ❌; otherwise any soft issue → ⚠️ Borderline; all-pass → ✅. GPA uses a 0.2 tolerance band, which is what makes "Borderline" meaningful. Every verdict ships with the exact reason.

**4. How do you prevent hallucinations?**
The decisions that matter are **not** LLM-generated. Eligibility verdicts, match scores, and deadline math are deterministic rule logic — reproducible and auditable. The LLM only does extraction and document drafting, and the Application Agent is constrained to use only facts from the student's profile (no invented credentials). Verdicts are identical with or without an LLM.

**5. How does fallback mode work?**
`get_llm_or_none()` returns an LLM only if a key is set. Without one, Profile uses regex extraction, Discovery uses the curated library, Application uses templates, and Eligibility/Match/Tracker are already deterministic. The full pipeline runs end-to-end offline. Deadline math uses a fixed reference date, so the demo is reproducible and never shows past-due dates.

**6. How does match scoring work?**
A transparent weighted formula: `0.30 × eligibility + 0.25 × academic_fit + 0.20 × goals_fit + 0.15 × skills_fit + 0.10 × urgency`. Each subscore is 0–1; the total renders as a percentage with a per-card breakdown. Eligibility is weighted highest (no point ranking something you can't win); urgency is a tiebreaker so closing deadlines surface.

**7. What makes this different from scholarship search websites?**
Search sites give you a filtered list and leave the hard part to you. Kairos *reasons about the student specifically*: it tells you **why** you're eligible or not (rule-level), ranks by personalized fit, **writes** your tailored application materials, and **prioritizes** what to do first by deadline. It's an agent that completes the workflow, not a directory you have to work through.

---

## 3. Live Demo Script (2.5–3 minutes)

> **Setup:** backend on `:8000`, frontend on `:5173`, browser at the Kairos home screen. Use **Demo Mode** — never a live upload on stage.

**[0:00–0:20] Hook.**
> "Every year, billions in scholarships go unclaimed — not because students don't qualify, but because checking eligibility across hundreds of programs and tailoring every application takes hours. Meet Maya: an international, first-generation, pre-med undergraduate. Watch Kairos do her week of work in under three minutes."

**[0:20–0:40] One click → autonomous run.**
> Click **🚀 Run Demo**. "She uploads her résumé once. Now the agent takes over." Let the live narration scroll — *Reading the résumé… Searching scholarships that match Maya's goals… Screening opportunities against eligibility…*

**[0:40–1:30] The money moment — explainable eligibility.**
> "It didn't just search — it *reasoned*." Point at a ❌: *"Not eligible — requires US citizenship, and Maya's international."* Then the ⚠️: *"Borderline — GPA 3.7, needs 3.8 — but everything else passes."* Then a ✅: *"Eligible, and here's why it fits her."*
> "Three verdicts, each with the exact reason. No scholarship site tells you this."

**[1:30–2:10] Top recommendation + tailored application.**
> Show the top recommendation with its score breakdown. Open a generated document: "A résumé, cover letter, and statement of purpose — written for *this* scholarship's mission, using only Maya's real background."

**[2:10–2:40] Action plan.**
> "Finally, it prioritizes." Point at the plan: *"Apply to the Global Health Corps Fellowship first — only 10 days left."* "It decides what to do first."

**[2:40–3:00] Close on impact (and the kicker).**
> "A week of work, in three minutes — and everything you just saw ran with **no API key**: the eligibility reasoning is deterministic and reproducible. For students like Maya, that's the difference between giving up and getting funded. That's Kairos."

---

## 4. Submission Checklist

### Repository
- [ ] Code pushed to the submission repo; default branch is clean.
- [ ] `README.md` present at root (✅ included).
- [ ] `docs/ARCHITECTURE.md` and `docs/SUBMISSION.md` present (✅ included).
- [ ] No secrets committed; `.env` is git-ignored (verify a root `.gitignore` covers `.env`, `.venv/`, `node_modules/`, `__pycache__/`).
- [ ] `LICENSE` / usage note added if required by the form.

### README
- [ ] Title, problem, solution, features, architecture, workflow present (✅).
- [ ] Setup + Demo Mode instructions verified on a clean machine.
- [ ] Screenshots embedded (see below).

### Environment variables
- [ ] `.env.example` documents `OPENAI_API_KEY`, `SERPAPI_KEY`, `ANTHROPIC_API_KEY`, `DEMO_REFERENCE_DATE` (✅).
- [ ] Confirmed the app runs with **no** keys (deterministic fallback).

### Demo Mode verification
- [ ] `🚀 Run Demo` completes end-to-end with no key set.
- [ ] Maya produces **all three** verdicts (✅ / ⚠️ / ❌), including the Borderline.
- [ ] No past-due deadlines / negative "days left" appear.
- [ ] Narration reads as an assistant (no `[AgentName]` log prefixes).

### Test suite verification
- [ ] `cd backend && python -m pytest -q` → **39 passed**.

### Screenshots needed
- [ ] `docs/screenshots/01-profile-upload.png`
- [ ] `docs/screenshots/02-agent-console.png` (live narration)
- [ ] `docs/screenshots/03-eligibility.png` (✅ ⚠️ ❌ cards with reasons)
- [ ] `docs/screenshots/04-match-scores.png` (score + breakdown)
- [ ] `docs/screenshots/05-action-plan.png`

### Architecture diagram needed
- [ ] Export the workflow diagram (README Mermaid) to `docs/screenshots/architecture.png` for forms that don't render Mermaid.

### Submission artifacts
- [ ] 50 / 150 / 400-word descriptions pasted into the form (✅ provided).
- [ ] Demo video recorded (follow the 3-minute script) and linked.
- [ ] Live URL or run instructions provided.
- [ ] Team names / track selection completed.
