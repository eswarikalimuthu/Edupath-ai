"""
EduPath AI - Document Management
Upload, validate, index, and manage educational reference materials for grounded RAG.
"""

import streamlit as st
from components.navbar import render_sidebar
from components.cards import render_header
from api_client import api_client

st.set_page_config(page_title="EduPath AI - Document Management", page_icon="📁", layout="wide")
render_sidebar()

render_header(title="Document Management & Knowledge Ingestion", subtitle="Upload and inspect official educational documents and career benchmark PDFs")

user = st.session_state.get("user")
if not user:
    st.warning("⚠️ Please sign in to manage documents.")
    st.stop()

# Upload Form
with st.container():
    st.subheader("📤 Ingest New Educational Document")
    uploaded_file = st.file_uploader(
        "Upload PDF, TXT, or Markdown Document (Max 15MB)",
        type=["pdf", "txt", "md"],
        help="Files will undergo recursive chunking, embeddings, and vector indexing in ChromaDB."
    )
    doc_desc = st.text_input("Document Description (Optional)", placeholder="e.g. Official University Curriculum, Industry Certification Syllabus")

    if st.button("🚀 Ingest & Index Document", use_container_width=True):
        if not uploaded_file:
            st.error("Please select a file to upload.")
        else:
            with st.spinner("Extracting text, cleaning, generating embeddings, and updating vector index..."):
                file_bytes = uploaded_file.read()
                res = api_client.upload_document(
                    file_bytes=file_bytes,
                    filename=uploaded_file.name,
                    description=doc_desc
                )
                if res["status_code"] == 201:
                    data = res["data"]
                    st.success(f"Successfully indexed '{data.get('filename')}' ({data.get('chunk_count')} chunks created)!")
                    st.rerun()
                else:
                    st.error(res["data"].get("detail", "Document ingestion failed."))

st.divider()

# Existing Ingested Documents List
st.subheader("📚 Active Knowledge Base Documents")
docs = api_client.get_documents()

if not docs:
    st.info("No documents uploaded yet.")
else:
    for d in docs:
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 1])
            with c1:
                st.markdown(f"📄 **{d.get('filename')}**")
                if d.get("description"):
                    st.caption(d.get("description"))
            with c2:
                st.write(f"Size: `{d.get('file_size') / 1024:.1f} KB`")
            with c3:
                st.write(f"Chunks: `{d.get('chunk_count')}`")
            with c4:
                is_global = d.get("is_global", False)
                badge = "🌐 Global System" if is_global else "🔒 My Document"
                st.write(badge)
            with c5:
                # Only owner or admin can delete
                if not is_global or user.get("role") == "admin":
                    if st.button("🗑️", key=f"del_doc_{d.get('id')}"):
                        api_client.delete_document(d.get("id"))
                        st.success("Document deleted")
                        st.rerun()
            st.write("---")
