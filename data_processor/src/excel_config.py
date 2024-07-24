import streamlit as st
import pandas as pd
import datetime
import requests
import boto3
from botocore.exceptions import NoCredentialsError


def download_config(file_name, label, mime):

    url = f"https://vehicle-ancestry-bucket-654654324108.s3.amazonaws.com/{file_name}"
    response = requests.get(url, stream=True)
    response.raise_for_status()
    data = response.content.decode("utf-8")

    timestamp = datetime.datetime.now().strftime("%d_%m_%YT%H_%M_%S")
    file_name_with_timestamp = f"{file_name.split('.')[0]}_{timestamp}.csv"
    st.download_button(
        label=label,
        data=data,
        file_name=file_name_with_timestamp,
        mime=mime,
    )


def upload_config(uploaded_file):
    if uploaded_file is not None:
        url = "https://vehicle-ancestry-bucket-654654324108.s3.amazonaws.com/excel_mappings.csv"
        response = requests.put(url, data=uploaded_file)
        if response.status_code == 200:
            st.success("File uploaded successfully.")
        else:
            st.error(f"Failed to upload file. Status code: {response.status_code}")


def app():
    st.title("Excel Config")

    # Download the current config
    download_config(
        "excel_mappings.csv",
        "Download Excel Column Mappings",
        "text/csv",
    )

    # Upload a new config
    uploaded_file = st.file_uploader("Upload a new config CSV", type="csv")
    if uploaded_file is not None:
        upload_config(uploaded_file)

    # Display the current config
    st.write("Current Excel Column Mappings:")
    df_mappings = pd.read_csv("data_processor/data/excel_mappings.csv")
    st.dataframe(df_mappings)


if __name__ == "__main__":
    app()
