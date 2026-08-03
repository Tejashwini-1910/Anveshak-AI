"""Optional OpenAI proposal writer. The app remains fully usable without it."""
from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen


class OpenAIProposalWriter:
    """Uses the Responses API only when both required environment variables exist."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL")

    @property
    def available(self) -> bool:
        return bool(self.api_key and self.model)

    def draft(self, query: str, themes: list[str], gaps: list[str], evidence: list[str]) -> str | None:
        if not self.available:
            return None
        prompt = (
            "Write a concise, evidence-aware research proposal draft. Treat every gap as a hypothesis, "
            "do not invent sources, and state limitations.\n"
            f"Question: {query}\nThemes: {', '.join(themes)}\n"
            f"Candidate gaps: {'; '.join(gaps)}\nEvidence titles: {'; '.join(evidence)}"
        )
        payload = json.dumps({"model": self.model, "input": prompt, "max_output_tokens": 900}).encode("utf-8")
        request = Request(
            "https://api.openai.com/v1/responses",
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
        if isinstance(result.get("output_text"), str):
            return result["output_text"].strip()
        for output in result.get("output", []):
            for content in output.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    return content["text"].strip()
        return None
