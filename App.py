import streamlit as st
from pypdf import PdfReader

st.set_page_config(
    page_title="Research Paper Assistant",
    page_icon="📚"
)

st.title("📚 Research Paper Assistant")
st.write("Upload a PDF research paper and read its contents.")

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_file:

    try:
        pdf_reader = PdfReader(uploaded_file)

        text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        st.success("PDF Loaded Successfully")

        st.subheader("Preview")

        if len(text) > 3000:
            st.text_area(
                "Extracted Text",
                text[:3000] + "...",
                height=400
            )
        else:
            st.text_area(
                "Extracted Text",
                text,
                height=400
            )

        st.subheader("Statistics")

        words = len(text.split())
        chars = len(text)

        col1, col2 = st.columns(2)

        col1.metric("Words", words)
        col2.metric("Characters", chars)

    except Exception as e:
        st.error(f"Error: {e}")
