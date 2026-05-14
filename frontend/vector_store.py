from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from frontend.document_loader import load_documents


def create_vector_db():

    documents = load_documents("data/consignes")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    db = FAISS.from_documents(
        chunks,
        embeddings
    )

    db.save_local("vector_db")

    return db


def load_vector_db():

    embeddings = OpenAIEmbeddings()

    db = FAISS.load_local(
        "vector_db",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db