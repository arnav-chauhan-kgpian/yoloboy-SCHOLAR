# Kairos — Architecture (for Judges)

A concise technical reference to how Kairos works under the hood.

---

## 1. Design Principles

1. **Blackboard multi-agent system.** Agents never call each other. They read from and write to a single shared `SessionState`. A LangGraph `StateGraph` owns sequencing. This makes the system debuggable, resumable, and demo-safe.
2. **LLM proposes, deterministic logic disposes.** Where it matters (eligibility verdicts, match scores, deadline math), the decision is **rule-based and reproducible**. The LLM is used for extraction and document generation, not for verdicts — so results are consistent and defensible.
3. **Key-optional.** Every agent has a deterministic fallback, so the full pipeline runs with **no API key**.

---

## 2. Agent Descriptions

| Agent | Input | Output | Notes |
|---|---|---|---|
| **Profile Agent** | Raw résumé text | Structured `StudentProfile` (name, GPA, major, degree level, citizenship, skills, goals) + confidence + missing fields | LLM extraction, or regex-based deterministic extraction. |
| **Discovery Agent** | Profile | Candidate `Opportunity[]` with pre-parsed eligibility criteria | Queries a curated knowledge base of **101 opportunities**; optional LLM augmentation. Never returns empty. |
| **Eligibility Agent** | Profile + opportunities | Per-opportunity verdict (✅/⚠️/❌) + rule-level reasons + eligibility score | **The differentiator.** Deterministic adjudication (see §4). |
| **Match Agent** | Profile + eligibility | Ranked opportunities with a 0–1 match score + subscores | Weighted formula (see §5). |
| **Application Agent** | Profile + top matches | Tailored résumé, cover letter, SOP per opportunity | LLM generation, or template fallback. Anti-fabrication: documents use only profile facts. |
| **Tracker Agent** | Ranked matches | Prioritized action plan (immediate / upcoming / watchlist) | Deadline math against a fixed reference date (see §6). |

---

## 3. LangGraph Workflow

```
START → profile → discovery → eligibility → matching → application → tracker → END
```

- Implemented as a LangGraph `StateGraph` over a typed `SessionState`.
- Each node is a pure `state → partial-state-update` function; conditional edges advance the phase.
- All nodes append to an **append-only narration stream** that the frontend renders live via Server-Sent Events (`GET /api/start-session/{id}`).
- Single-writer discipline: each agent writes only its own slice of state (`profile`, `opportunities`, `eligibility_results`, `match_result`, `application_results`, `tracker_result`).

---

## 4. Eligibility Engine (the differentiator)

A two-layer design that separates fuzzy interpretation from deterministic adjudication.

**Per-rule evaluation.** For each opportunity, the engine checks four rule families against the profile:
- **Citizenship** — symmetric: it parses the *allowed* set (US citizen / permanent resident / international / DACA) and passes only if the student is in it. Correctly rejects both "US-only" awards for international students **and** "international-only" awards for US citizens.
- **GPA** — a hard floor **with a 0.2 tolerance band**.
- **Degree level** — hard match.
- **Field of study** — hard match (with fuzzy term overlap).

**Severity.** Each failing rule is tagged `hard` (disqualifying) or `soft` (borderline / near-miss).

**Deterministic rollup:**

| Condition | Verdict | Score |
|---|---|---|
| Any **hard** rule fails | ❌ Not Eligible | 0.0 |
| No hard fail, any **soft** issue | ⚠️ Borderline | 0.55–0.75 |
| All rules pass | ✅ Eligible | 1.0 |

**Exact reasons.** The verdict ships with a human-readable, rule-level reason, e.g.:
- ❌ *"Requires US Citizen or Permanent Resident. Student = International Student."*
- ⚠️ *"GPA 3.7 is just under the 3.8 requirement (within 0.2)."*

The GPA tolerance is what makes the **Borderline** category meaningful: a near-miss is a careful "maybe," not a hard rejection.

---

## 5. Match Scoring

Applied to non-rejected opportunities. Each subscore is 0–1; the weighted total is shown as a percentage.

```
match_score = 0.30 × eligibility
            + 0.25 × academic_fit
            + 0.20 × goals_fit
            + 0.15 × skills_fit
            + 0.10 × urgency
```

- **eligibility** — from the engine (1.0 eligible / 0.55–0.75 borderline / 0.0 rejected). Weighted highest: no point ranking something the student can't win.
- **academic_fit** — field + degree-level alignment.
- **goals_fit** — overlap between the student's stated goals and the opportunity's mission.
- **skills_fit** — overlap between student skills and required skills.
- **urgency** — deadline proximity (rewards actionable-now).

Ties break by urgency, then amount. Rankings sort on the raw 0–1 score, so display scale never affects order.

---

## 6. Fallback Mode (key-optional)

`get_llm_or_none()` returns an LLM only if a key is configured; otherwise every agent degrades gracefully:

| Agent | With LLM | Without LLM (fallback) |
|---|---|---|
| Profile | LLM extraction | Regex/deterministic extraction |
| Discovery | Curated KB + LLM augmentation | Curated knowledge base only |
| Eligibility | Deterministic | Deterministic (identical) |
| Match | Deterministic | Deterministic (identical) |
| Application | LLM-written documents | Template-based documents |
| Tracker | Deterministic | Deterministic (identical) |

**Determinism extras:** deadline math uses a fixed `DEMO_REFERENCE_DATE` (default `2026-01-05`) so urgency and "days left" are reproducible and never show past-due dates on stage.

**Why this matters for judging:** the eligibility verdicts and match scores — the parts judges scrutinize — are deterministic and identical with or without a key. The demo cannot hang on a network call and cannot show an empty board.
