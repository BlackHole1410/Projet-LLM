import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from rag.chat.chroma import Querry  # Import the Querry function

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API depuis les variables d'environnement
api_key = os.getenv("GEMINI_API_KEY")  # Assurez-vous que votre clé est dans .env sous GEMINI_API_KEY

if not api_key:
    st.error("Clé API manquante. Assurez-vous que GEMINI_API_KEY est défini dans le fichier .env.")
else:
    # Initialiser l'API Google Gemini avec votre clé API
    genai.configure(api_key=api_key)

    # Interface Streamlit
    st.title("Chatbot RAG - Contrats d'Assurances")
    st.write("Posez vos questions sur les contrats d'assurances")

    # Champ de saisie pour la question
    prompt = st.chat_input("Entrez votre question")

    # Fonction pour formater le prompt
    def format_prompt(question: str) -> str:
        return f"You are an assitant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences and keep the answer concise. Question : {question}. Context {Querry(question)}. Answer :"  # Simple pass-through for now

    # Fonction pour générer une réponse en utilisant l'API Google Gemini
    def generate_answer(formatted_prompt: str) -> str:
        return "Réponse générée par Google Gemini"  # Placeholder response

    # Si une question est posée
    if prompt:
        st.write(f"Question posée : {prompt}")

        # Étape 1: Formatage du prompt
        formatted_prompt = format_prompt(prompt)

        # Étape 2: Utilisation de la fonction Querry pour obtenir des résultats
        query_results = Querry(formatted_prompt)

        # Affichage des résultats de la requête
        st.write("Résultats de la requête :", query_results)

        # Étape 3: Génération de la réponse avec Google Gemini
        answer = generate_answer(formatted_prompt)

        # Affichage de la réponse générée
        st.write("Réponse générée :", answer)