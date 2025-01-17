import streamlit as st
import os
import uuid  # For unique keys in feedback
from dotenv import load_dotenv
import google.generativeai as genai
from rag.chat.chroma import dict_to_chroma, chroma_query
from streamlit_feedback import streamlit_feedback

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Configure Streamlit page
st.title("💬 Chatbot RAG - Contrats d'Assurances")
st.caption("Posez vos questions sur les documents.")

# Initialize ChromaDB
dict_to_chroma()

# Initialize session state for messages if not present
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Comment puis-je vous aider ?"}
    ]

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

# Initialize session state for chat history and feedback state
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "fbk" not in st.session_state:
    st.session_state["fbk"] = str(uuid.uuid4())  # Unique key for feedback component

import json

# Function to save feedback to JSON
def save_feedback_to_json(feedback_score, filename="feedback.json"):
    """Save the feedback score (emoji) to a JSON file."""
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
def handle_feedback(feedback_response):
    """Update the chat history with feedback and save only the emoji to a JSON file."""
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


# Function to handle feedback submission
# def handle_feedback(feedback_response):
#     """Update the chat history with feedback and log only the score to the terminal."""
#     if st.session_state["chat_history"]:  # Ensure history exists
#         last_entry = st.session_state["chat_history"][-1]  # Get the last message
#         last_entry.update({"feedback": feedback_response["score"]})  # Add feedback score to the last message
#         st.session_state["chat_history"][-1] = last_entry  # Update session state
        
#         # Log only the score to the terminal/command prompt
#         print(f"Feedback score received: {feedback_response['score']}")
            
#     # Reset feedback key for new feedback
#     st.session_state["fbk"] = str(uuid.uuid4())


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

    # Format the prompt
    def format_prompt(question: str, context: str) -> str:
        return (
            f"You are an assistant for question-answering tasks. "
            f"Use the following pieces of retrieved context to answer the question. "
            f"If you don't know the answer, just say 'Je ne sais pas.'. "
            f"Use up to three sentences maximum if needed, otherwise use less. Keep the answer concise. "
            f"Question: {question}. Context: {context}."
        )

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
    st.chat_message("assistant").write(assistant_response)

    # Feedback component for the assistant's response
    feedback_response = streamlit_feedback(
        feedback_type="faces",  # Faces feedback system
        key=st.session_state["fbk"],  # Unique key
        on_submit=handle_feedback  # Handle feedback submission
    )
