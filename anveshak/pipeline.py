from datetime import datetime, timezone
from .agents import CitationNetworkAgent, HallucinationVerificationAgent, KnowledgeGraphAgent, LiteratureRetrievalAgent, NoveltyAssessmentAgent, PDFUnderstandingAgent, ProposalGenerationAgent, ResearchGapAgent, SemanticAnalysisAgent
from .llm import OpenAIProposalWriter

class ResearchCoordinatorAgent:
    name = "Research Coordinator Agent"
    def plan(self, query, domains): return {"query": query, "domains": domains or ["General scientific literature"], "goal": "Find evidence, generate cautious insights, and preserve provenance."}

class ResearchPipeline:
    def run(self, query: str, domains: list[str] | None = None, uploads: list[dict] | None = None) -> dict:
        progress = []
        coordinator = ResearchCoordinatorAgent(); plan = coordinator.plan(query, domains or []); progress.append({"agent": coordinator.name, "status": "completed"})
        retriever = LiteratureRetrievalAgent(); papers, sources = retriever.search(query); progress.append({"agent": retriever.name, "status": "completed", "detail": f"{len(papers)} papers from {', '.join(sources)}"})
        uploads = uploads or []
        pdf = PDFUnderstandingAgent().run(papers, uploads); progress.append({"agent": PDFUnderstandingAgent.name, "status": "completed", "detail": f"{len(uploads)} uploaded PDF(s) processed"})
        uploaded_text = " ".join(item.get("text", "") for item in uploads)
        semantic = SemanticAnalysisAgent().run(papers, uploaded_text); progress.append({"agent": SemanticAnalysisAgent.name, "status": "completed"})
        graph = KnowledgeGraphAgent().run(papers, semantic["themes"]); progress.append({"agent": KnowledgeGraphAgent.name, "status": "completed"})
        citations = CitationNetworkAgent().run(papers); progress.append({"agent": CitationNetworkAgent.name, "status": "completed"})
        novelty = NoveltyAssessmentAgent().run(query, papers); progress.append({"agent": NoveltyAssessmentAgent.name, "status": "completed"})
        gaps = ResearchGapAgent().run(semantic["themes"], novelty); progress.append({"agent": ResearchGapAgent.name, "status": "completed"})
        proposal = ProposalGenerationAgent().run(query, semantic["themes"], gaps)
        writer = OpenAIProposalWriter()
        if writer.available:
            try:
                draft = writer.draft(query, [theme["name"] for theme in semantic["themes"]], gaps["candidate_gaps"], [paper.title for paper in papers[:6]])
                if draft:
                    proposal["llm_draft"] = draft
                    proposal["generation"] = f"LLM proposal draft via {writer.model}"
            except Exception:
                proposal["llm_status"] = "LLM draft unavailable; deterministic outline retained."
        else:
            proposal["llm_status"] = "Optional LLM draft is disabled. Set OPENAI_API_KEY and OPENAI_MODEL in .env to enable it."
        progress.append({"agent": ProposalGenerationAgent.name, "status": "completed", "detail": proposal["generation"]})
        verification = HallucinationVerificationAgent().run(proposal, papers); progress.append({"agent": HallucinationVerificationAgent.name, "status": "completed"})
        return {"title": "Anveshak AI — Explainable Research Report", "generated_at": datetime.now(timezone.utc).isoformat(), "plan": plan, "progress": progress, "sources": sources, "papers": [p.public() for p in papers], "pdf_understanding": pdf, "semantic_analysis": semantic, "knowledge_graph": graph, "citation_network": citations, "novelty_assessment": novelty, "research_gaps": gaps, "proposal": proposal, "verification": verification}
