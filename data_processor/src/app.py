import streamlit as st
from pdf_processor import app as pdf_processor
from excel_processor import app as excel_processor
from pdf_config import app as pdf_config
from excel_config import app as excel_config

# Set the page to wide mode
st.set_page_config(layout="wide")

# Define the navigation structure
apps = {
    "PDF Processor": "pdf_processor",
    "Excel Processor": "excel_processor",
    "PDF Config": "pdf_config",
    "Excel Config": "excel_config",
}

# Add a simple login page
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username == "admin" and password == "vehicleancestry":
        # Add a selectbox to the sidebar for navigation
        selected_app = st.sidebar.selectbox("Choose an app", list(apps.keys()))

        if selected_app == "PDF Config":
            pdf_config()
        elif selected_app == "Excel Config":
            excel_config()
        elif selected_app == "PDF Processor":
            pdf_processor()
        elif selected_app == "Excel Processor":
            excel_processor()
    else:
        st.error("Incorrect username or password")
# Add other navigation options here
