import streamlit as st
import json
import os
from collections import Counter

# Load feedback data from JSON file
feedback_file = os.path.join(os.path.dirname(__file__), '..', 'feedback.json')
with open(feedback_file, 'r') as f:
    feedback_data = json.load(f)

# Count the occurrences of each feedback emoji
feedback_counts = Counter(feedback_data)

# Create a Streamlit dashboard
st.title("Tableau de bord des feedbacks")
st.write("Ceci est un tableau de bord exprimant les feedbacks des utilisateurs.")

# Display feedback counts
st.write("### Nombre de feedbacks")
for emoji, count in feedback_counts.items():
    st.write(f"{emoji}: {count}")

# Display total feedback count
total_feedback = sum(feedback_counts.values())
st.write(f"**Total des feedbacks :** {total_feedback}")

# Display a bar chart of feedback counts
st.write("### Distribution des feedbacks")
st.bar_chart(feedback_counts)