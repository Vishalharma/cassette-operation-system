import streamlit as st
from PyPDF2 import PdfReader

# Page Config
st.set_page_config(
    page_title="Research Paper Assistant",
    page_icon="📚",
    layout="wide"
)

# Title
st.title("📚 Research Paper Assistant")
st.write("Upload a research paper PDF and analyze its contents.")

# Upload PDF
uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)

if uploaded_file is not None:

    try:
        pdf_reader = PdfReader(uploaded_file)

        text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        st.success("✅ PDF uploaded successfully!")

        # Statistics
        word_count = len(text.split())
        char_count = len(text)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Words", word_count)

        with col2:
            st.metric("Total Characters", char_count)

        st.subheader("📄 Extracted Text")

        st.text_area(
            "Content",
            text[:10000],
            height=500
        )

        # Search Feature
        st.subheader("🔍 Search in Paper")

        keyword = st.text_input("Enter keyword")

        if keyword:
            if keyword.lower() in text.lower():
                st.success(f"'{keyword}' found in document")
            else:
                st.warning(f"'{keyword}' not found")

    except Exception as e:
        st.error(f"Error reading PDF: {e}")

else:
    st.info("Upload a PDF file to begin.")
