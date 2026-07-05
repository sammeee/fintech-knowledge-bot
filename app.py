# app.py
import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Fintech Knowledge Bot",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Fintech Regulatory Knowledge Bot")
st.markdown("Upload fintech regulatory PDFs and ask questions about their contents.")

# Sidebar — document upload
with st.sidebar:
    st.header("📄 Document Upload")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Ingest Document"):
            with st.spinner("Ingesting document..."):
                response = requests.post(
                    f"{API_URL}/ingest",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                )
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ {data['message']}")
                st.info(f"Chunks added: {data['chunks_added']}")
            else:
                st.error(f"Error: {response.text}")

    st.divider()
    st.markdown("### How to use")
    st.markdown("1. Upload a regulatory PDF")
    st.markdown("2. Click **Ingest Document**")
    st.markdown("3. Ask questions in the chat")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📎 Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

# Chat input
if question := st.chat_input("Ask a question about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # Get answer from API
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question}
            )
        
        if response.status_code == 200:
            data = response.json()
            st.write(data["answer"])
            
            if data["sources"]:
                with st.expander("📎 Sources"):
                    for source in data["sources"]:
                        st.write(f"- {source}")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": data["answer"],
                "sources": data["sources"]
            })
        else:
            st.error("Error connecting to the API.")