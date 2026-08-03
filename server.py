from __future__ import annotations

import json
import base64
import io
import re
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from anveshak.pipeline import ResearchPipeline

ROOT = Path(__file__).parent
WEB = ROOT / "web"
MAX_PDF_BYTES = 15 * 1024 * 1024


def extract_pdf_upload(item: dict) -> dict:
    name = Path(str(item.get("name", "document.pdf"))).name
    raw = base64.b64decode(item.get("content", ""), validate=True)
    if len(raw) > MAX_PDF_BYTES:
        raise ValueError(f"{name} exceeds the 15 MB PDF upload limit.")
    if not raw.startswith(b"%PDF"):
        raise ValueError(f"{name} is not a valid PDF file.")
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return {"name": name, "pages": len(reader.pages), "text": text[:120000], "status": "text extracted"}
    except ImportError:
        # Keeps the upload path usable during setup, but makes extraction status transparent.
        preview = " ".join(match.decode("latin-1", "ignore") for match in re.findall(rb"[A-Za-z][A-Za-z0-9 ,.;:()/-]{30,}", raw))
        return {"name": name, "pages": None, "text": preview[:12000], "status": "basic preview only — install pypdf for full extraction"}


class AnveshakHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        requested = urlparse(path).path.lstrip("/") or "index.html"
        return str(WEB / requested)

    def do_POST(self) -> None:
        if self.path != "/api/research":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            query = str(payload.get("query", "")).strip()
            if len(query) < 8:
                raise ValueError("Please enter a research question of at least 8 characters.")
            uploads = [extract_pdf_upload(item) for item in payload.get("uploads", [])]
            report = ResearchPipeline().run(query=query, domains=payload.get("domains", []), uploads=uploads)
            data = json.dumps(report, ensure_ascii=False).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_error(HTTPStatus.BAD_REQUEST, str(exc))
        except Exception as exc:  # Keep server errors informative during early development.
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Pipeline failed: {exc}")

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    print("Anveshak AI is ready at http://localhost:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), AnveshakHandler).serve_forever()
