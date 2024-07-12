import streamlit as st
import pandas as pd
import datetime


def download_config(file_path, label, file_name, mime):
    timestamp = datetime.datetime.now().strftime("%d_%m_%YT%H_%M_%S")
    file_name_with_timestamp = f"{file_name.split('.')[0]}_{timestamp}.csv"
    st.download_button(
        label=label,
        data=open(file_path, "r").read(),
        file_name=file_name_with_timestamp,
        mime=mime,
    )


def upload_config(uploaded_file):
    if uploaded_file is not None:
        with open("data_processor/data/pdf_config.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Config file uploaded successfully!")


def app():
    st.title("PDF Config")

    # Download the current config
    download_config(
        "data_processor/data/pdf_config.csv",
        "Download PDF Config",
        "pdf_config.csv",
        "text/csv",
    )

    # Upload a new config
    uploaded_file = st.file_uploader("Upload a new config CSV", type="csv")
    if uploaded_file is not None:
        upload_config(uploaded_file)

    # Display the current config
    st.write("Current PDF Config:")
    pdf_config = pd.read_csv("data_processor/data/pdf_config.csv", index_col=0)
    st.dataframe(pdf_config)


if __name__ == "__main__":
    app()
