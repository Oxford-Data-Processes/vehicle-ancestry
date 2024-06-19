import streamlit as st
from pdf_processor import (
    app as pdf_processor,
)  # Assuming you have a function called `process_pdf` in your pdf_processor module

# Set the page to wide mode
st.set_page_config(layout="wide")

# Define the navigation structure
apps = {
    "Home": "home",
    "PDF Processor": "pdf_processor",
    # Add other apps here
}

# Add a selectbox to the sidebar for navigation
selected_app = st.sidebar.selectbox("Choose an app", list(apps.keys()))


# Define the Home page
def home():
    st.write("Welcome to the Home Page!")


# Add other app functions here

# Navigation
if selected_app == "Home":
    home()
elif selected_app == "PDF Processor":
    pdf_processor()
# Add other navigation options here
