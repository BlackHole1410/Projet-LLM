import streamlit as st
import os

st.set_page_config(layout="centered", initial_sidebar_state="collapsed")
html_folder = "documents"
file_path = os.path.join(html_folder, 'OptiSecure Assurances - Incendie domestique.html')
with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()
    st.components.v1.html(html_content, height=600, scrolling=True)
