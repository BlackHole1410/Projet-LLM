import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

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
        return f"Question: {question}\nRéponse:"

    # Fonction pour générer une réponse en utilisant l'API Google Gemini
    def generate_answer(formatted_prompt: str) -> str:
        try:
            # Récupérer le modèle Gemini supporté pour la génération de contenu
            model = genai.GenerativeModel('gemini-pro')

            # Initialiser le chat avec un historique vide
            chat = model.start_chat(history=[])

            # Envoi du message et récupération de la réponse
            response = chat.send_message(formatted_prompt, stream=True)

            # Traitement de la réponse en streaming
            answer = ""
            for chunk in response:
                if chunk.text:
                    answer += chunk.text

            return answer.strip()
        except Exception as e:
            st.error(f"Erreur lors de la génération de la réponse : {e}")
            return "Erreur lors de la génération de la réponse."

    # Si une question est posée
    if prompt:
        st.write(f"Question posée : {prompt}")

        # Étape 1: Formatage du prompt
        formatted_prompt = format_prompt(prompt)

        # Étape 2: Génération de la réponse avec Google Gemini
        answer = generate_answer(formatted_prompt)

        # Affichage de la réponse générée
        st.write("Réponse générée :", answer)
