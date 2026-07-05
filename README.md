---
title: Fintech Knowledge Bot
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: apache-2.0
---

# 📚 Fintech Regulatory Knowledge Bot

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58%2B-red)
![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-yellow)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-purple)
![Docker](https://img.shields.io/badge/Docker-Containerised-blue)

A production-ready RAG-powered chatbot that answers questions about fintech regulatory documents. Upload any PDF, ask questions, and get answers with source citations — all powered by a two-service FastAPI + Streamlit architecture.

---

## 🏗️ Architecture

```text
┌─────────────────────┐         HTTP          ┌─────────────────────┐
│  Streamlit Frontend │ ────────────────────> │   FastAPI Backend   │
│     (Port 8501)      │   POST /ingest       │     (Port 8000)     │
│                      │   POST /ask          │                     │
│  - PDF upload UI     │   GET  /health       │  - RAG pipeline     │
│  - Chat interface    │                      │  - ChromaDB storage │
│  - Source citations  │                      │  - LangChain chains │
└─────────────────────┘                       └─────────────────────┘
```


---

## ✨ Key Features

- 📄 **PDF Ingestion** — upload any regulatory PDF and ingest it into the knowledge base
- 🔍 **Semantic Search** — ChromaDB vector store with `all-MiniLM-L6-v2` embeddings
- 🤖 **RAG Pipeline** — LangChain LCEL chain with Qwen2.5-7B-Instruct via HuggingFace
- 📎 **Source Citations** — every answer shows which document and page it came from
- 💬 **Chat Interface** — full conversation history with Streamlit chat components
- 🐳 **Dockerised** — FastAPI backend containerised and ready for cloud deployment
- ⚡ **REST API** — production FastAPI backend with Swagger docs at `/docs`

---

## 🛠️ Technologies Used

- **FastAPI** — REST API backend with Pydantic validation and auto-generated Swagger docs
- **Streamlit** — interactive chat frontend
- **LangChain** — RAG pipeline with LCEL
- **ChromaDB** — local vector database for semantic search
- **Sentence Transformers** — `all-MiniLM-L6-v2` for document embeddings
- **Qwen2.5-7B-Instruct** — LLM for answer generation via HuggingFace Inference API
- **PyPDF** — PDF loading and parsing
- **Docker** — containerisation for production deployment

---

## 🗂️ Project Structure

```text
fintech-knowledge-bot/
├── api/
│   ├── main.py          # FastAPI backend — endpoints and request/response models
│   ├── rag.py           # RAG pipeline — ingest, embed, retrieve, generate
│   └── __init__.py
├── app.py               # Streamlit frontend — chat UI and API communication
├── Dockerfile           # Container definition for FastAPI backend
├── requirements.txt     # Python dependencies
└── README.md
```


---

## 🚀 How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/sammeee/fintech-knowledge-bot.git
cd fintech-knowledge-bot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Start the FastAPI backend (Terminal 1)**
```bash
$env:HF_TOKEN="your_token_here"   # Windows PowerShell
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**4. Start the Streamlit frontend (Terminal 2)**
```bash
streamlit run app.py
```

**5. Open the app**

Go to **http://localhost:8501** in your browser.

FastAPI Swagger docs available at **http://localhost:8000/docs**

---

## 🐳 Docker Deployment

**Build and run the FastAPI backend with Docker:**
```bash
docker build -t fintech-knowledge-bot .
docker run -p 8000:8000 -e HF_TOKEN=your_token_here fintech-knowledge-bot
```

Then run the Streamlit frontend separately and point it at the containerised backend.

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/ingest` | Upload and ingest a PDF |
| POST | `/ask` | Ask a question against ingested docs |

Full interactive API documentation available at `http://localhost:8000/docs`

---

## 🔮 Future Improvements

- [ ] Persistent ChromaDB storage across restarts
- [ ] Multi-document management — list and delete ingested documents
- [ ] Docker Compose to orchestrate frontend and backend together
- [ ] Cloud deployment to AWS EC2 or Google Cloud Run
- [ ] Authentication and rate limiting on the API
- [ ] Streaming responses for faster perceived latency

---

## 📋 Results & Observations

- Chunk size of 512 tokens with 64-token overlap balances retrieval precision and context
- Temperature of 0.1 keeps answers grounded in retrieved documents
- Source citations help users verify answers against original regulatory text
- Two-service architecture allows frontend and backend to scale independently

---

*Apache 2.0 License*

## 🚀 Try It Now
**Live Demo → [Fintech Knowledge Bot on Hugging Face Spaces](https://szamadesh-fintech-knowledge-bot.hf.space)**