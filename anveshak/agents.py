from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

STOPWORDS = {"about", "after", "among", "and", "are", "can", "for", "from", "how", "into", "its", "of", "on", "or", "the", "to", "using", "what", "with"}

@dataclass
class Paper:
    title: str; authors: str; year: int | None; venue: str; abstract: str; citations: int; url: str; source: str
    def public(self) -> dict[str, Any]: return asdict(self)

def keywords(text: str, limit: int = 12) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z-]{2,}", text.lower())
    return [word for word, _ in Counter(w for w in words if w not in STOPWORDS).most_common(limit)]

class LiteratureRetrievalAgent:
    name = "Literature Retrieval Agent"
    def search(self, query: str) -> tuple[list[Paper], list[str]]:
        papers, sources = [], []
        try:
            url = f"https://api.crossref.org/works?query={quote(query)}&rows=8&select=title,author,published,container-title,abstract,is-referenced-by-count,URL"
            for item in self._get(url)["message"]["items"]:
                title = (item.get("title") or [""])[0]
                if title:
                    authors = ", ".join(f"{a.get('given','')} {a.get('family','')}".strip() for a in item.get("author", [])[:3]) or "Unknown"
                    year = item.get("published", {}).get("date-parts", [[None]])[0][0]
                    papers.append(Paper(title, authors, year, (item.get("container-title") or [""])[0], re.sub("<.*?>", "", item.get("abstract", "")), item.get("is-referenced-by-count", 0), item.get("URL", ""), "Crossref"))
            sources.append("Crossref")
        except Exception: pass
        try:
            for item in self._get(f"https://api.openalex.org/works?search={quote(query)}&per-page=8")["results"]:
                papers.append(Paper(item["title"], ", ".join(a["author"]["display_name"] for a in item.get("authorships", [])[:3]) or "Unknown", item.get("publication_year"), item.get("primary_location", {}).get("source", {}).get("display_name", ""), "Abstract indexed by OpenAlex." if item.get("abstract_inverted_index") else "", item.get("cited_by_count", 0), item.get("doi") or item.get("id", ""), "OpenAlex"))
            sources.append("OpenAlex")
        except Exception: pass
        if not papers:
            topic = " ".join(keywords(query, 5)).title() or "Research Innovation"
            papers = [Paper(f"{topic}: a systematic research agenda", "Anveshak Demonstration Group", 2025, "Research Innovation Review", "A demonstration record used when scholarly sources are unavailable.", 24, "", "Local demonstration corpus"), Paper(f"Infrastructure and innovation pathways for {topic}", "Anveshak Demonstration Group", 2024, "SDG Systems Journal", "A demonstration record used when scholarly sources are unavailable.", 13, "", "Local demonstration corpus")]
            sources.append("Local demonstration corpus")
        return list({p.title.lower(): p for p in papers}.values())[:12], sources
    @staticmethod
    def _get(url: str) -> dict[str, Any]:
        with urlopen(Request(url, headers={"User-Agent": "AnveshakAI/0.1 (research prototype)"}), timeout=6) as response: return json.load(response)

class PDFUnderstandingAgent:
    name = "PDF Understanding Agent"
    def run(self, papers: list[Paper]) -> dict: return {"status": "ready", "summary": "Metadata and available abstracts were structured for analysis. Upload parsing can be enabled with pypdf.", "documents_processed": len(papers)}

class SemanticAnalysisAgent:
    name = "Semantic Analysis Agent"
    def run(self, papers: list[Paper]) -> dict:
        terms = Counter()
        for paper in papers: terms.update(keywords(paper.title + " " + paper.abstract, 20))
        return {"themes": [{"name": word.title(), "mentions": count} for word, count in terms.most_common(8)], "method": "transparent frequency-based semantic baseline"}

class KnowledgeGraphAgent:
    name = "Knowledge Graph Agent"
    def run(self, papers: list[Paper], themes: list[dict]) -> dict:
        nodes = [{"id": f"p{i}", "label": p.title[:56], "type": "paper"} for i, p in enumerate(papers)] + [{"id": f"t{i}", "label": t["name"], "type": "theme"} for i, t in enumerate(themes[:6])]
        links = [{"source": f"p{i}", "target": f"t{j}", "relation": "discusses"} for i, p in enumerate(papers) for j, t in enumerate(themes[:6]) if t["name"].lower() in (p.title + " " + p.abstract).lower()]
        return {"nodes": nodes, "links": links}

class CitationNetworkAgent:
    name = "Citation Network Agent"
    def run(self, papers: list[Paper]) -> dict:
        ranked = sorted(papers, key=lambda p: p.citations, reverse=True)
        return {"most_influential": [{"title": p.title, "citations": p.citations} for p in ranked[:5]], "note": "Counts are source-provided references, not a complete citation graph."}

class NoveltyAssessmentAgent:
    name = "Novelty Assessment Agent"
    def run(self, query: str, papers: list[Paper]) -> dict:
        absent = sorted(set(keywords(query)) - set(keywords(" ".join(p.title + " " + p.abstract for p in papers), 50)))
        score = min(92, 40 + len(absent) * 12)
        return {"score": score, "interpretation": "promising" if score >= 64 else "adjacent to established work", "unrepresented_query_terms": absent, "caveat": "Transparent screening signal, not a patentability or publication guarantee."}

class ResearchGapAgent:
    name = "Research Gap Agent"
    def run(self, themes: list[dict], novelty: dict) -> dict:
        gaps = [f"Test how {t['name'].lower()} relates to the research question with a reproducible dataset." for t in themes[-3:]]
        gaps += [f"Evaluate the underrepresented concept '{term}' against existing methods." for term in novelty["unrepresented_query_terms"][:2]]
        return {"candidate_gaps": gaps or ["Collect more evidence before claiming a specific gap."], "warning": "Gaps are hypotheses grounded in this retrieval set and require human validation."}

class ProposalGenerationAgent:
    name = "Proposal Generation Agent"
    def run(self, query: str, themes: list[dict], gaps: dict) -> dict:
        names = ", ".join(t["name"] for t in themes[:4]) or "the retrieved themes"
        return {"title": f"Evidence-based investigation of {query.rstrip('?')}", "objective": f"Develop and evaluate an approach addressing: {query}", "research_questions": [query, "Which measurable factors explain the observed outcomes?", "How does the approach compare with a transparent baseline?"], "methodology": f"Review evidence around {names}; define a dataset, build a baseline, evaluate with pre-registered metrics, and report limitations.", "expected_contribution": gaps["candidate_gaps"][0]}

class HallucinationVerificationAgent:
    name = "Hallucination Verification Agent"
    def run(self, proposal: dict, papers: list[Paper]) -> dict:
        checks = [{"claim": "The report uses retrieved scholarly metadata as evidence.", "confidence": .9 if papers else .2, "evidence": [p.title for p in papers[:3]]}, {"claim": proposal["expected_contribution"], "confidence": .55, "evidence": ["Candidate gap inferred from retrieved theme distribution."]}]
        return {"checks": checks, "overall_confidence": round(sum(c["confidence"] for c in checks) / len(checks), 2), "policy": "Claims without direct source support are labelled as proposals or hypotheses."}
