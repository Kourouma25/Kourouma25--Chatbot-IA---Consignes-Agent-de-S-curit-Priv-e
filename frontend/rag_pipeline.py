from langchain_openai import ChatOpenAI

from frontend.vector_store import load_vector_db
from frontend.prompts import SYSTEM_PROMPT


def get_chatbot_response(question: str):
    db = load_vector_db()

    docs = db.similarity_search(question, k=3)

    context = "\n\n".join([
        f"Source: {doc.metadata}\nContenu: {doc.page_content}"
        for doc in docs
    ])

    prompt = f"""
{SYSTEM_PROMPT}

Voici les consignes disponibles :

{context}

Question utilisateur :
{question}

Réponds uniquement à partir des consignes ci-dessus.
"""

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    response = llm.invoke(prompt)

    return response.content, docs