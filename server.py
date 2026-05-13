import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn

from core.orchestrator import ConsultingOrchestrator

app = FastAPI(title="Consulting Agent AI")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

orchestrator = ConsultingOrchestrator()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class AnalyzeRequest(BaseModel):
    company: str
    question: str
    ticker: Optional[str] = None


class EngageRequest(BaseModel):
    issue: str
    company: str = ""
    ticker: str = ""
    issue_type: str = ""
    conversation: list = []


class RunAnalysisRequest(BaseModel):
    issue: str
    company: str = ""
    ticker: str = ""
    issue_type: str = ""
    conversation: list = []


@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.post("/api/analyze")
async def analyze_json(req: AnalyzeRequest):
    result = orchestrator.run_structured(
        company=req.company,
        question=req.question,
        ticker=req.ticker or None,
    )
    return result


@app.post("/api/analyze-with-files")
async def analyze_with_files(
    company: str = Form(...),
    question: str = Form(...),
    ticker: Optional[str] = Form(None),
    files: list[UploadFile] = File(None),
):
    saved_files = []
    if files:
        for f in files:
            if f.filename:
                ext = os.path.splitext(f.filename)[1].lower()
                if ext in (".pdf", ".txt", ".md", ".csv", ".json", ".html"):
                    dest = os.path.join(UPLOAD_DIR, f.filename)
                    content = await f.read()
                    with open(dest, "wb") as out:
                        out.write(content)
                    saved_files.append(dest)

    result = orchestrator.run_structured(
        company=company,
        question=question,
        ticker=ticker or None,
        documents=saved_files or None,
    )

    for sf in saved_files:
        try:
            os.remove(sf)
        except Exception:
            pass

    return result


@app.post("/api/engage")
async def engage(req: EngageRequest):
    result = orchestrator.engage(
        issue=req.issue,
        company=req.company,
        ticker=req.ticker,
        conversation=req.conversation,
        issue_type=req.issue_type or None,
    )
    return result


@app.post("/api/run-analysis")
async def run_analysis(req: RunAnalysisRequest):
    result = orchestrator.run_issue_analysis(
        issue=req.issue,
        company=req.company,
        ticker=req.ticker,
        issue_type=req.issue_type,
        conversation=req.conversation,
    )
    return result


@app.post("/api/run-analysis-with-files")
async def run_analysis_with_files(
    issue: str = Form(...),
    company: str = Form(...),
    ticker: str = Form(""),
    issue_type: str = Form(""),
    conversation: str = Form("[]"),
    files: list[UploadFile] = File(None),
):
    import json
    conv = json.loads(conversation)
    saved_files = []
    if files:
        for f in files:
            if f.filename:
                ext = os.path.splitext(f.filename)[1].lower()
                if ext in (".pdf", ".txt", ".md", ".csv", ".json"):
                    dest = os.path.join(UPLOAD_DIR, f.filename)
                    content = await f.read()
                    with open(dest, "wb") as out:
                        out.write(content)
                    saved_files.append(dest)

    result = orchestrator.run_issue_analysis(
        issue=issue,
        company=company,
        ticker=ticker,
        issue_type=issue_type,
        conversation=conv,
        documents=saved_files or None,
    )

    for sf in saved_files:
        try:
            os.remove(sf)
        except Exception:
            pass

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
