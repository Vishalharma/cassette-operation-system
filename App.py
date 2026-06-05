import streamlit as st
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI

st.set_page_config(page_title="Research Paper Assistant")

st.title("📚 Research Paper RAG Assistant")

pdf = st.file_uploader("Upload Research Paper", type="pdf")

if pdf:

    reader = PdfReader(pdf)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(text)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_texts(chunks, embeddings)

    st.success("Paper Loaded Successfully")

    query = st.text_input("Ask Question About Paper")

    if query:

        docs = vector_store.similarity_search(query)

        llm = ChatOpenAI(
            api_key="YOUR_OPENAI_API_KEY",
            model="gpt-4o-mini"
        )

        chain = load_qa_chain(llm, chain_type="stuff")

        answer = chain.run(
            input_documents=docs,
            question=query
        )

        st.write("### Answer")
        st.write(answer)
