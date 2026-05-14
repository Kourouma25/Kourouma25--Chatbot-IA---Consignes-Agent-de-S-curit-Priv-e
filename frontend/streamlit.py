import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
from dotenv import load_dotenv

from frontend.vector_store import create_vector_db
from frontend.rag_pipeline import get_chatbot_response

load_dotenv()

API_URL = "http://127.0.0.1:8000"

DATA_DIR = Path("data/consignes")
VECTOR_DB_DIR = Path("vector_db")

st.set_page_config(
    page_title="Assistant IA - Consignes Sécurité",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 34px;
    font-weight: 800;
}
.subtitle {
    font-size: 17px;
    color: #555;
}
.source-box {
    background-color: #f8fafc;
    padding: 12px;
    border-radius: 10px;
    border-left: 4px solid #2563eb;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "email" not in st.session_state:
    st.session_state.email = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None


def login_backend(email, password):
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )

        if response.status_code == 200:
            return response.json(), None

        try:
            error_detail = response.json().get("detail", response.text)
        except Exception:
            error_detail = response.text

        return None, f"Erreur backend {response.status_code} : {error_detail}"

    except requests.exceptions.ConnectionError:
        return None, "Backend indisponible. Lance : uvicorn backend.main:app --reload"
    except Exception as e:
        return None, str(e)


def create_user_backend(nom, prenom, email, password, role):
    try:
        response = requests.post(
            f"{API_URL}/users/create",
            json={
                "nom": nom,
                "prenom": prenom,
                "email": email,
                "password": password,
                "role": role
            },
            timeout=10
        )

        if response.status_code == 200:
            return response.json(), None

        try:
            error_detail = response.json().get("detail", response.text)
        except Exception:
            error_detail = response.text

        return None, f"Erreur backend {response.status_code} : {error_detail}"

    except requests.exceptions.ConnectionError:
        return None, "Backend indisponible. Lance : uvicorn backend.main:app --reload"
    except Exception as e:
        return None, str(e)


def logout():
    st.session_state.authenticated = False
    st.session_state.messages = []
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.email = None
    st.session_state.user_id = None
    st.rerun()


def login_page():
    st.markdown(
        '<div class="main-title">🛡️ Assistant Consignes Sécurité</div>',
        unsafe_allow_html=True
    )

    st.write("Connectez-vous ou créez un compte agent / responsable.")

    tab1, tab2 = st.tabs(["🔐 Connexion", "➕ Créer un compte"])

    with tab1:
        st.markdown("### Connexion")

        with st.form("login_form"):
            email = st.text_input(
                "Email de connexion",
                placeholder="agent@test.com",
                key="login_email"
            )

            password = st.text_input(
                "Mot de passe",
                type="password",
                key="login_password"
            )

            login_submitted = st.form_submit_button(
                "Se connecter",
                use_container_width=True
            )

            if login_submitted:
                if not email.strip() or not password.strip():
                    st.warning("Veuillez saisir votre email et votre mot de passe.")
                else:
                    data, error = login_backend(email.strip(), password.strip())

                    if error:
                        st.error(error)
                    else:
                        st.session_state.authenticated = True
                        st.session_state.token = data["access_token"]
                        st.session_state.role = data["role"]
                        st.session_state.email = data["email"]
                        st.session_state.user_id = data["user_id"]
                        st.rerun()

    with tab2:
        st.markdown("### Créer un nouvel utilisateur")

        with st.form("create_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                nom = st.text_input("Nom", key="create_nom")
                prenom = st.text_input("Prénom", key="create_prenom")

            with col2:
                new_email = st.text_input(
                    "Email",
                    placeholder="exemple@test.com",
                    key="create_email"
                )

                new_password = st.text_input(
                    "Mot de passe",
                    type="password",
                    key="create_password"
                )

            role = st.selectbox(
                "Type de compte",
                ["agent", "responsable"],
                key="create_role"
            )

            submitted = st.form_submit_button(
                "Créer le compte",
                use_container_width=True
            )

            if submitted:
                if not nom.strip() or not prenom.strip() or not new_email.strip() or not new_password.strip():
                    st.warning("Veuillez remplir tous les champs.")
                else:
                    data, error = create_user_backend(
                        nom.strip(),
                        prenom.strip(),
                        new_email.strip(),
                        new_password.strip(),
                        role
                    )

                    if error:
                        st.error(error)
                    else:
                        st.success("Compte créé avec succès. Vous pouvez maintenant vous connecter.")


if not st.session_state.authenticated:
    login_page()
    st.stop()


with st.sidebar:
    st.title("🛡️ Assistant Sécurité")

    st.success(f"Connecté : {st.session_state.email}")
    st.info(f"Rôle : {st.session_state.role}")

    if st.button("Se déconnecter", use_container_width=True):
        logout()

    st.divider()

    st.markdown("### 📂 Base documentaire")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    files = list(DATA_DIR.glob("*"))
    valid_files = [
        f for f in files
        if f.suffix.lower() in [".txt", ".pdf", ".docx"]
    ]

    st.metric("Documents disponibles", len(valid_files))

    with st.expander("Voir les documents"):
        if valid_files:
            for file in valid_files:
                st.write(f"📄 {file.name}")
        else:
            st.warning("Aucun document trouvé.")

    if st.session_state.role == "responsable":
        uploaded_files = st.file_uploader(
            "Ajouter des consignes",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = DATA_DIR / uploaded_file.name

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            st.success("Document(s) ajouté(s).")

        if st.button("🔄 Indexer / Mettre à jour la base", use_container_width=True):
            with st.spinner("Indexation des documents..."):
                create_vector_db()

            st.success("Base vectorielle mise à jour.")

    else:
        st.info("Mode agent : vous pouvez consulter les consignes mais pas modifier la base documentaire.")

    st.divider()

    st.markdown("### ⚙️ Informations")

    if VECTOR_DB_DIR.exists():
        st.success("Base vectorielle disponible")
    else:
        st.error("Base vectorielle non créée")

    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


st.markdown(
    '<div class="main-title">🛡️ Chatbot IA - Consignes Agent de Sécurité Privée</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Assistant intelligent pour rechercher rapidement les procédures : accès, rondes, incendie, incidents, main courante...</div>',
    unsafe_allow_html=True
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📄 Documents", len(valid_files))

with col2:
    st.metric(
        "💬 Questions posées",
        len([m for m in st.session_state.messages if m["role"] == "user"])
    )

with col3:
    status = "Active" if VECTOR_DB_DIR.exists() else "À indexer"
    st.metric("🧠 Base IA", status)

st.divider()

st.markdown("### 💡 Exemples de questions")

ex1, ex2, ex3 = st.columns(3)

with ex1:
    if st.button("Que faire en cas d’incendie ?"):
        st.session_state.example_question = "Que doit faire l’agent en cas d’incendie ?"

with ex2:
    if st.button("Comment gérer une intrusion ?"):
        st.session_state.example_question = "Quelle est la procédure en cas d’intrusion ?"

with ex3:
    if st.button("Que noter dans la main courante ?"):
        st.session_state.example_question = "Que doit noter l’agent dans la main courante ?"

st.markdown("### 💬 Discussion")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Posez une question sur les consignes...")

if "example_question" in st.session_state:
    question = st.session_state.example_question
    del st.session_state.example_question

if question:
    if not VECTOR_DB_DIR.exists():
        st.error("Veuillez d'abord indexer les documents depuis la barre latérale.")
    else:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Recherche dans les consignes..."):
                answer, sources = get_chatbot_response(question)

            st.write(answer)

            with st.expander("📚 Sources utilisées"):
                for i, source in enumerate(sources, start=1):
                    metadata = source.metadata
                    content = source.page_content[:600]

                    st.markdown(
                        f"""
                        <div class="source-box">
                        <b>Source {i}</b><br>
                        <b>Fichier :</b> {metadata.get("source", "Non précisé")}<br><br>
                        <b>Extrait :</b><br>
                        {content}...
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })