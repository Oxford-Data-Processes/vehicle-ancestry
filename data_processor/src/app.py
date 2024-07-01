import streamlit as st
from pdf_processor import app as pdf_processor
from excel_processor import app as excel_processor
from pdf_config import app as pdf_config
from excel_config import app as excel_config

# Set the page to wide mode and light mode
st.set_page_config(layout="wide", theme="light")

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

# Check if the login was successful
if st.experimental_get_query_params().get("login") == ["success"]:
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
    if st.button("Login"):
        if username == "admin" and password == "vehicleancestry":
            # Save the login status to cookies
            st.experimental_set_query_params({"login": "success"})
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password")
    else:
        st.error("Please login to access the application.")
