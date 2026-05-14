from pathlib import Path

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader
)


def load_documents(folder_path: str):

    documents = []

    folder = Path(folder_path)

    for file in folder.glob("*"):

        if file.suffix.lower() == ".txt":

            loader = TextLoader(
                str(file),
                encoding="utf-8"
            )

            documents.extend(loader.load())

        elif file.suffix.lower() == ".pdf":

            loader = PyPDFLoader(str(file))

            documents.extend(loader.load())

        elif file.suffix.lower() == ".docx":

            loader = Docx2txtLoader(str(file))

            documents.extend(loader.load())

    return documents