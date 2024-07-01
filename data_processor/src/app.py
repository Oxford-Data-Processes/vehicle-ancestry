import streamlit as st
from pdf_processor import (
    app as pdf_processor,
    pdf_config,
)
from excel_processor import app as excel_processor, excel_config

# Set the page to wide mode
st.set_page_config(layout="wide")

# Define the navigation structure
apps = {
    "Home": "home",
    "PDF Processor": "pdf_processor",
    "Excel Processor": "excel_processor",
    # Add other apps here
}

# Add a selectbox to the sidebar for navigation
selected_app = st.sidebar.selectbox("Choose an app", list(apps.keys()))


def home(config):
    st.write("Welcome to the Home Page!")
    st.write("PDF Config:")
    st.json(pdf_config, expanded=False)
    st.write("Excel Config:")
    st.json(excel_config, expanded=False)


# Add other app functions here

# Navigation
if selected_app == "Home":
    home(pdf_config)
elif selected_app == "PDF Processor":
    pdf_processor()
elif selected_app == "Excel Processor":
    excel_processor()
# Add other navigation options here
