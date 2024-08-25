import streamlit as st
from pdf_processor import app as pdf_processor
from excel_processor import app as excel_processor
from pdf_config import app as pdf_config
from excel_config import app as excel_config
from typing import Dict


# Dummy user credentials
USER_CREDENTIALS: Dict[str, str] = {
    "admin": "vehicleancestry",
}


def login() -> None:
    """
    Display the login page and handle user authentication.
    """
    st.title("Login")
    username: str = st.text_input("Username")
    password: str = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")


def main_app() -> None:
    """
    Display the main application interface after successful login.
    """
    st.set_page_config(layout="wide")

    # Define the navigation structure
    apps: Dict[str, str] = {
        "PDF Processor": "pdf_processor",
        "Excel Processor": "excel_processor",
        "PDF Config": "pdf_config",
        "Excel Config": "excel_config",
    }

    # Add a selectbox to the sidebar for navigation
    selected_app: str = st.sidebar.selectbox("Choose an app", list(apps.keys()))

    if selected_app == "PDF Config":
        pdf_config()
    elif selected_app == "Excel Config":
        excel_config()
    elif selected_app == "PDF Processor":
        pdf_processor()
    elif selected_app == "Excel Processor":
        excel_processor()


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login()
