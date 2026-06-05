import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="PDF Assistant", page_icon="📚")

st.title("📚 Research PDF Assistant")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    pdf = PdfReader(uploaded_file)

    text = ""

    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    st.success("PDF Loaded Successfully ✅")

    st.subheader("📄 Preview")
    st.text_area("Extracted Text", text[:8000], height=400)

    st.subheader("📊 Stats")
    st.metric("Words", len(text.split()))
    st.metric("Characters", len(text))
