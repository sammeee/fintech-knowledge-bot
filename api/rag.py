# api/rag.py
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
import tempfile

# Embedding model — loaded once at startup
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

# In-memory vector store — resets on restart
# For production you would use PersistentClient
vectorstore = None

def ingest_pdf(file_bytes: bytes, filename: str) -> int:
    """Load a PDF, chunk it, and add to the vector store. Returns chunk count."""
    global vectorstore

    # Write bytes to a temp file so PyPDFLoader can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    documents = loader.load()

    # Add source metadata
    for doc in documents:
        doc.metadata["source"] = filename

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=64,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents)

    if vectorstore is None:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name="fintech_kb"
        )
    else:
        vectorstore.add_documents(chunks)

    return len(chunks)


def build_rag_chain():
    """Build and return the RAG chain."""
    if vectorstore is None:
        return None

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    llm_endpoint = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        task="conversational",
        max_new_tokens=512,
        temperature=0.1,
        huggingfacehub_api_token=os.environ.get("HF_TOKEN")
    )
    llm = ChatHuggingFace(llm=llm_endpoint)

    prompt = ChatPromptTemplate.from_template("""
You are a fintech regulatory expert assistant. Answer the question based ONLY 
on the following context from regulatory documents. If you cannot find the answer 
in the context, say "I don't have enough information in the uploaded documents 
to answer this question."

Always cite which document your answer comes from.

Context:
{context}

Question: {question}

Answer:""")

    def format_docs(docs):
        return "\n\n---\n\n".join(
            f"[Source: {doc.metadata.get('source', 'Unknown')}, "
            f"Page: {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
            for doc in docs
        )

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever


def query(question: str) -> dict:
    """Run a question through the RAG pipeline and return answer + sources."""
    result = build_rag_chain()
    if result is None:
        return {
            "answer": "Please upload a document first.",
            "sources": []
        }

    chain, retriever = result
    answer = chain.invoke(question)
    source_docs = retriever.invoke(question)

    sources = list({
        f"{doc.metadata.get('source', 'Unknown')} "
        f"(Page {doc.metadata.get('page', 'N/A')})"
        for doc in source_docs
    })

    return {"answer": answer, "sources": sources}