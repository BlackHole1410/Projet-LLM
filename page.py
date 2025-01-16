import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from rag.chat.chroma import Querry  # Importer la fonction Querry depuis chroma.py

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

        # Appel à la fonction Querry pour obtenir le contexte
        context_results = Querry(question)  # Obtenir les résultats de la requête
        context = context_results["documents"][0][0] if context_results["documents"] else "Aucun contexte trouvé."

        # Formater le prompt avec la question et le contexte
        return f"Vous êtes un assistant pour les tâches de questions-réponses. Utilisez les éléments de contexte suivants récupérés pour répondre à la question. Si vous ne connaissez pas la réponse, dites simplement que vous ne la connaissez pas. Utilisez trois phrases maximum et gardez la réponse concise. Question: {question}. Contexte : {context}. Réponse:"

    # Fonction pour générer une réponse en utilisant l'API Google Gemini
    def generate_answer(formatted_prompt: str) -> str:
        return "Réponse générée par Google Gemini"  # Placeholder response

    # Si une question est posée
    if prompt:
        st.write(f"Question posée : {prompt}")

        # Étape 1: Formatage du prompt avec le contexte récupéré
        formatted_prompt = format_prompt(prompt)

        # Étape 2: Utilisation de la fonction Querry pour obtenir des résultats
        query_results = Querry(formatted_prompt)

        # Affichage des résultats de la requête
        st.write("Résultats de la requête :", query_results)

        # Étape 3: Génération de la réponse avec Google Gemini
        answer = generate_answer(formatted_prompt)

        # Affichage de la réponse générée
        st.write("Réponse générée :", answer)