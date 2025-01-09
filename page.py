import streamlit as st
from google import genai
from google.genai import types

# Récupérer la clé API depuis les variables d'environnement
client = genai.Client(api_key="GEMINI_API_KEY")

# Interface Streamlit
st.title("Chatbot RAG")
st.write("Posez vos questions sur les contrats d'assurances")




# Champ de saisie pour la question
prompt = st.chat_input("Entrer votre question")

# Fonction pour générer une réponse à partir de la question
def generate_answer(question: str) -> str:
    # Créer une requête
    request = types.QueryRequest(
        query=question,
        model="text-bison-001",  # Assurez-vous que le modèle est correct
        max_output_tokens=200
    )
    
    # Appeler l'API
    response = client.query(request)
    
    # Récupérer et retourner la réponse
    return response.result

if prompt:
    st.write(prompt)
    
    # Générer et afficher la réponse
    answer = generate_answer(prompt)
    st.write("Réponse générée :", answer)



### Erreur quand il veut répondre, de plus il réécrase la question si une deuxième est posée