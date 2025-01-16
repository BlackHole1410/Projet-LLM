import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from rag.chat.chroma import dict_to_chroma, chroma_query

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Configure Streamlit page
st.title("💬 Chatbot RAG - Contrats d'Assurances")
st.caption("Posez vos questions sur les documents.")

# Initialize ChromaDB
dict_to_chroma()

# Sidebar for file upload
with st.sidebar:
    uploaded_file = st.file_uploader("Choisissez un document HTML", type=["html"], accept_multiple_files=False)
    if uploaded_file:
        bytes_data = uploaded_file.read()
        file_path = os.path.join('./documents', uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(bytes_data)
        st.write("Fichier téléchargé et enregistré sous :", uploaded_file.name)
        # Reinitialize ChromaDB with the new document
        dict_to_chroma()

# Initialize session state for messages if not present
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Comment puis-je vous aider ?"}
    ]

# Display chat history
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Input prompt
prompt = st.chat_input("Entrez votre question")
if prompt:
    if not api_key:
        st.error("Clé API manquante. Assurez-vous que GEMINI_API_KEY est défini dans le fichier .env.")
        st.stop()

    # Append user message to session state
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Format prompt
    def format_prompt(question: str, context: str) -> str:
        return (
            f"You are an assistant for question-answering tasks. "
            f"Use the following pieces of retrieved context to answer the question. "
            f"If you don't know the answer, just say 'Je ne sais pas.'. "
            f"Use up to three sentences maximum if needed, otherwise use less. Keep the answer concise. "
            f"Question: {question}. Context: {context}."
        )

    # Query ChromaDB for context
    context = chroma_query(prompt)

    # Generate answer using Google Gemini
    formatted_prompt = format_prompt(prompt, context)

    try:
        # Generate a response
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(formatted_prompt)
        answer = response.choices[0].text if response.choices else "Je ne sais pas."
    except Exception as e:
        answer = f"Erreur lors de la génération de la réponse : {e}"

    # Append assistant's response to session state and display it
    st.session_state["messages"].append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)