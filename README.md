# Anveshak AI

Anveshak AI is a human-centred research exploration platform for SDG 9 — *Industry, Innovation and Infrastructure*. It coordinates specialist AI agents to retrieve literature, analyse evidence, identify gaps, assess novelty, and generate an explainable research report.

## Run locally

Prerequisite: Python 3.10+.

```powershell
python server.py
```

Open `http://localhost:8000`. Enter a research question and select **Run research pipeline**. The first run uses public Crossref and OpenAlex data when reachable; a curated fallback keeps demonstrations usable offline.

## Agent workflow

1. Research Coordinator — interprets the question and plans the run.
2. Literature Retrieval — searches Crossref and OpenAlex.
3. PDF Understanding — extracts structured text from supplied documents (ready for `pypdf` when installed).
4. Semantic Analysis — clusters themes and key terms.
5. Knowledge Graph — creates transparent paper/theme/evidence relationships.
6. Citation Network — derives citation influence links.
7. Novelty Assessment — compares proposed terms with the evidence base.
8. Research Gap — identifies underexplored themes.
9. Proposal Generation — drafts an evidence-aware proposal outline.
10. Hallucination Verification — checks report claims against retrieved evidence and attaches confidence.

## Optional enhancements

Set these environment variables before starting the server to add higher-quality source access:

- `SEMANTIC_SCHOLAR_API_KEY`
- `OPENAI_API_KEY` (to replace the deterministic local writing helpers with an LLM)

## Project layout

- `server.py` — standard-library web server and API.
- `anveshak/agents.py` — isolated, testable specialist agent implementations.
- `anveshak/pipeline.py` — coordinator and pipeline orchestration.
- `web/` — accessible browser interface.
- `tests/` — smoke tests for the research pipeline.

## Version control

```powershell
git init
git add .
git commit -m "feat: bootstrap Anveshak AI research agent platform"
```

Create an empty GitHub repository, then connect it:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/anveshak-ai.git
git push -u origin main
```
