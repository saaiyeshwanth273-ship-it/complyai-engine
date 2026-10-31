from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from complyai.api.app import ComplyAIApplication
from complyai.connectors.india import IndiaConnector
from complyai.db.repository import RegulatoryRepository
from complyai.ingestion.pipeline import RegulatoryIngestionService

# --------------------------------------------------
# Initialize ComplyAI with a local in-memory repository
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

repository = RegulatoryRepository()

ingestion = RegulatoryIngestionService(repository=repository)
india_documents = ingestion.ingest_all_from_connector(IndiaConnector())

compliance_app = ComplyAIApplication(repository=repository)

app = FastAPI(
    title="ComplyAI",
    description="Local compliance auditing prototype",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# --------------------------------------------------
# Dashboard
# --------------------------------------------------

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


# --------------------------------------------------
# API endpoints
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "running",
        "application": "ComplyAI",
        "loaded_india_documents": len(india_documents),
        "storage": "in-memory",
        "ai_backend": "mock",
    }


@app.get("/api/sources")
def sources():
    documents = repository.list_documents()

    return {
        "total": len(documents),
        "sources": [
            {
                "document_id": doc.document_id,
                "title": doc.title,
                "jurisdiction": doc.jurisdiction,
                "authority": doc.authority,
                "status": (
                    doc.status.value
                    if hasattr(doc.status, "value")
                    else str(doc.status)
                ),
                "sections": len(doc.sections),
                "source_url": doc.source_url,
            }
            for doc in documents
        ],
    }


@app.post("/api/audit")
def run_audit(payload: dict):
    document_text = payload.get("document_text", "").strip()

    if not document_text:
        raise HTTPException(
            status_code=400,
            detail="Please provide a policy or document to audit.",
        )

    try:
        result = compliance_app.handle_audit_request(payload)
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Audit failed: {str(exc)}",
        )


@app.post("/api/query")
def regulatory_query(payload: dict):
    query = payload.get("query", "").strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Please enter a regulatory question.",
        )

    try:
        return compliance_app.handle_query_request(
            query=query,
            jurisdiction=payload.get("jurisdiction"),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(exc)}",
        )


@app.get("/api/definition/{term}")
def definition(term: str):
    return compliance_app.handle_definition_lookup(term)