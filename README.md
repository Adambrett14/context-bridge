# Context Bridge

**Evidence-based AI handoff generator.** Context Bridge converts long AI
conversations, project histories, or messy working notes into a verified,
portable continuity package that a brand-new AI session can pick up and run
with — without inventing project state.

> **Status: M1 skeleton.** Demo fixtures and app shell in place. Live demo
> link, BYOK mode, and local LLM mode land in later milestones.

## How it works

Source material moves through a deterministic, auditable pipeline:
Source → 1. Atomic Memory Ledger → 2. Draft Continuity Capsule
→ 3. Capsule Audit → 4A/4B. Final Bridge Pack → 4C. YAML State
Every stage has an explicit contract. Conflicts are preserved, not silently
resolved. Suggestions are never promoted into decisions. The audit stage
checks the draft against the source before anything is finalized.

## Modes (v1 targets)

- **Demo Mode** — no API key needed; replays bundled, clearly-labeled sample
  outputs so the public link always works.
- **BYOK Mode** — bring your own key for any OpenAI-compatible provider.
  Keys are masked, runtime-only, never stored, logged, or exported.
- **Local LLM Mode** — clone the repo, run Ollama or another local
  OpenAI-compatible endpoint, keep private transcripts on your machine.

## Privacy posture

Context Bridge does not intentionally store transcripts or API keys. No
accounts, no database, no server-side history. External providers you connect
to have their own retention terms [VERIFY per provider].

## No hard app limits

Context Bridge sets no app-defined input/output size caps. Large runs may
still hit **external** provider/model/host/browser limits — those are
surfaced honestly as external failures, never disguised as app policy.

## Local setup

```bash
git clone <repo-url> && cd context-bridge
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
Run tests with pytest, lint with ruff check .
Roadmap
M1 skeleton ✅ → M2 demo pipeline → M3 live providers (BYOK/Ollama) →
M4 polish + public deployment. Phase 2 backlog: PDF/export importers,
per-stage providers, Docker, and more.
