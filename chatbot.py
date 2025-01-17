import streamlit as st
import os
import uuid 
from dotenv import load_dotenv
import google.generativeai as genai
import sys
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rag.chat.chroma import chroma_query
from rag.indexing.embedding import dict_to_chroma
from streamlit_feedback import streamlit_feedback

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Configure Streamlit page
st.title("💬 Chatbot RAG - Contrats d'Assurances")
st.caption("Posez vos questions sur les documents.")


# Initialize ChromaDB once during app startup
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

# Display chat messages from history
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])


# Initialize session state for chat history and feedback state
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "fbk" not in st.session_state:
    st.session_state["fbk"] = str(uuid.uuid4())  # Unique key for feedback component

import json

# Function to save feedback to JSON
def save_feedback_to_json(feedback_score: str, filename: str = "feedback.json") -> None:
    """
    Save the feedback score (emoji) to a JSON file.
    This function checks if the specified JSON file exists. If it does, it loads the existing data,
    appends the new feedback score to it, and then saves the updated data back to the file. If the
    file does not exist, it creates a new list with the feedback score and saves it to the file.
    Args:
        feedback_score (str): The feedback score represented as an emoji.
        filename (str, optional): The name of the JSON file to save the feedback to. Defaults to "feedback.json".
    Raises:
        Exception: If there is an error saving to the JSON file, an exception is caught and an error message is printed.
    """
    try:
        # Check if the file exists
        if os.path.exists(filename):
            # Load existing data from the JSON file
            with open(filename, "r") as json_file:
                data = json.load(json_file)
        else:
            # Create a new list if the file does not exist
            data = []

        # Append the new feedback score (emoji)
        data.append(feedback_score)

        # Save updated data to the JSON file
        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
    except Exception as e:
        print(f"Error saving to JSON: {e}")

# Function to handle feedback submission
def handle_feedback(feedback_response: dict) -> None:
    """
    Update the chat history with feedback and save only the emoji to a JSON file.
    Args:
        feedback_response (dict): A dictionary containing the feedback score (emoji).
    Returns:
        None
    """
    if st.session_state["chat_history"]:  # Ensure history exists
        last_entry = st.session_state["chat_history"][-1]  # Get the last assistant response
        feedback_score = feedback_response["score"]  # Get the emoji (score)

        # Update the session state with feedback
        last_entry.update({"feedback": feedback_score})
        st.session_state["chat_history"][-1] = last_entry

        # Save feedback emoji to the JSON file
        save_feedback_to_json(feedback_score)

        # Log feedback to the terminal/command prompt
        print(f"Feedback score received: {feedback_score}")

    # Reset feedback key for new feedback submissions
    st.session_state["fbk"] = str(uuid.uuid4())

# Display chat messages from history
for msg in st.session_state["chat_history"]:
    st.chat_message(msg["role"]).write(msg["content"])
    # Display feedback for each assistant's message
    if msg["role"] == "assistant" and "feedback" not in msg:
        # Feedback only for the latest assistant response without feedback
        feedback_response = streamlit_feedback(
            feedback_type="faces",  # Faces feedback system
            key=st.session_state["fbk"],  # Unique key
            on_submit=handle_feedback  # Handle feedback submission
        )

# Input prompt for user
prompt = st.chat_input("Entrez votre question")
if prompt:
    if not api_key:
        st.error("Clé API manquante. Assurez-vous que GEMINI_API_KEY est défini dans le fichier .env.")
        st.stop()

    # Append user message to chat history
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Query ChromaDB for context
    context = chroma_query(prompt)
    
    titles = []
    for document in context.get("documents", [[]])[0]:
        try:
            # Convertir le document en dictionnaire
            doc_data = eval(document)
            if "title" in doc_data:
                titles.append(doc_data["title"])
        except Exception as e:
            print(f"Erreur lors de l'extraction du titre : {e}")
            
    # Format the prompt
    def format_prompt(question: str, context: str) -> str:
        """
        Formats a prompt for a question-answering assistant.

        This function takes a question and a context string, and returns a formatted
        prompt that instructs the assistant on how to answer the question using the
        provided context. The assistant is instructed to keep the answer concise and
        to respond with "Je ne sais pas." if the answer is not known.

        Args:
            question (str): The question to be answered.
            context (str): The context information to be used for answering the question.

        Returns:
            str: A formatted prompt string for the assistant.
        """
        return (
            f"You are an assistant for question-answering tasks. "
            f"Use the following pieces of retrieved context to answer the question. "
            f"If you don't know the answer, just say 'Je ne sais pas.'. "
            f"Use up to three sentences maximum if needed, otherwise use less. Keep the answer concise. And in French. "
            f"Question: {question}. Context: {context}."
        )

    # Query ChromaDB for context
    context = chroma_query(prompt)
        
    titles = []
    for document in context.get("documents", [[]])[0]:
        try:
            # Convertir le document en dictionnaire
            doc_data = eval(document)
            if "title" in doc_data:
                titles.append(doc_data["title"])
        except Exception as e:
            print(f"Erreur lors de l'extraction du titre : {e}")
            
    # Generate answer using Google Gemini
    genai.configure(api_key=api_key)
    formatted_prompt = format_prompt(prompt, context)

    # Generate assistant's response
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(formatted_prompt)
        assistant_response = response.text
    except Exception as e:
        assistant_response = f"Erreur lors de la génération de la réponse : {e}"

    # Append assistant's response to chat history
    st.session_state["chat_history"].append({"role": "assistant", "content": assistant_response})
    st.chat_message("assistant").write(assistant_response + f"\n **Source : {titles[0]}**", unsafe_allow_html=True)

    # Feedback component for the assistant's response
    feedback_response = streamlit_feedback(
        feedback_type="faces",  # Faces feedback system
        key=st.session_state["fbk"],  # Unique key
        on_submit=handle_feedback  # Handle feedback submission
    )
