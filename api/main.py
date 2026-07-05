# api/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from api.rag import ingest_pdf, query

app = FastAPI(
    title="Fintech Knowledge Bot API",
    description="RAG-powered API for fintech regulatory document Q&A",
    version="1.0.0"
)

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]

class IngestResponse(BaseModel):
    message: str
    chunks_added: int

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "fintech-knowledge-bot"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """Upload and ingest a PDF document into the knowledge base."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_bytes = await file.read()
    chunks_added = ingest_pdf(file_bytes, file.filename)
    
    return IngestResponse(
        message=f"Successfully ingested {file.filename}",
        chunks_added=chunks_added
    )

@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """Ask a question against the ingested documents."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    result = query(request.question)
    return AnswerResponse(
        answer=result["answer"],
        sources=result["sources"]
    )