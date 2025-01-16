import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from rag.chat.chroma import dict_to_chroma, chroma_query

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Streamlit page
st.title("💬 Chatbot RAG - Contrats d'Assurances")
st.caption("Posez vos questions sur les documents.")

# Initialize ChromaDB once during app startup
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
    genai.configure(api_key=api_key)
    formatted_prompt = format_prompt(prompt, context)

    try:
        # Generate a response
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(formatted_prompt)
    except Exception as e:
        response = f"Erreur lors de la génération de la réponse : {e}"

    # Append assistant's response to session state and display it
    st.session_state["messages"].append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)