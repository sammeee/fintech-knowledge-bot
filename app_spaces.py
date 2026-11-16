# app.py — Single-service version for Hugging Face Spaces
import os
import tempfile
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq


st.set_page_config(
    page_title="Fintech Knowledge Bot",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Fintech Regulatory Knowledge Bot")
st.markdown("Upload fintech regulatory PDFs and ask questions about their contents.")

# Initialise session state
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs_ingested" not in st.session_state:
    st.session_state.docs_ingested = []

# Load embedding model once
@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

@st.cache_resource
def load_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=512,
        groq_api_key=os.environ.get("GROQ_API_KEY")
    )


embeddings = load_embeddings()

# Sidebar — document upload
with st.sidebar:
    st.header("📄 Document Upload")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Ingest Document"):
            with st.spinner("Ingesting document..."):
                # Write to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                loader = PyPDFLoader(tmp_path)
                documents = loader.load()

                for doc in documents:
                    doc.metadata["source"] = uploaded_file.name

                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=512,
                    chunk_overlap=64
                )
                chunks = splitter.split_documents(documents)

                if st.session_state.vectorstore is None:
                    st.session_state.vectorstore = Chroma.from_documents(
                        documents=chunks,
                        embedding=embeddings,
                        collection_name="fintech_kb"
                    )
                else:
                    st.session_state.vectorstore.add_documents(chunks)

                st.session_state.docs_ingested.append(uploaded_file.name)

            st.success(f"✅ Ingested {uploaded_file.name}")
            st.info(f"Chunks added: {len(chunks)}")

    if st.session_state.docs_ingested:
        st.divider()
        st.markdown("### 📁 Ingested Documents")
        for doc in st.session_state.docs_ingested:
            st.write(f"- {doc}")

    st.divider()
    st.markdown("### How to use")
    st.markdown("1. Upload a regulatory PDF")
    st.markdown("2. Click **Ingest Document**")
    st.markdown("3. Ask questions in the chat")

# Build RAG chain
def build_chain(vectorstore):
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    llm = load_llm()

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

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📎 Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

if question := st.chat_input("Ask a question about your documents..."):
    if st.session_state.vectorstore is None:
        st.warning("Please upload and ingest a document first.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                chain, retriever = build_chain(st.session_state.vectorstore)
                answer = chain.invoke(question)
                source_docs = retriever.invoke(question)
                sources = list({
                    f"{doc.metadata.get('source', 'Unknown')} "
                    f"(Page {doc.metadata.get('page', 'N/A')})"
                    for doc in source_docs
                })

            st.write(answer)
            if sources:
                with st.expander("📎 Sources"):
                    for source in sources:
                        st.write(f"- {source}")

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })
