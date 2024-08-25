import streamlit as st
import pandas as pd
import datetime
import requests
from io import StringIO
from typing import Optional
from variables import AWS_PRESIGNED_URL

def download_config(file_name: str, label: str, mime: str) -> str:
    """
    Download configuration file from S3 bucket and create a download button.

    Args:
        file_name (str): Name of the file to download.
        label (str): Label for the download button.
        mime (str): MIME type of the file.

    Returns:
        str: Content of the downloaded file.
    """
    url = f"{AWS_PRESIGNED_URL}/{file_name}"
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
    return data


def upload_config(uploaded_file: Optional[st.UploadedFile]) -> None:
    """
    Upload configuration file to S3 bucket.

    Args:
        uploaded_file (Optional[st.UploadedFile]): File uploaded by the user.
    """
    if uploaded_file is not None:
        url = f"{AWS_PRESIGNED_URL}/pdf_config.csv"
        response = requests.put(url, data=uploaded_file)
        if response.status_code == 200:
            st.success("File uploaded successfully.")
        else:
            st.error(f"Failed to upload file. Status code: {response.status_code}")


def app() -> None:
    """
    Main application function for PDF Config page.
    """
    st.title("PDF Config")

    # Download the current config
    data = download_config(
        "pdf_config.csv",
        "Download PDF Config",
        "text/csv",
    )

    # Upload a new config
    uploaded_file = st.file_uploader("Upload a new config CSV", type="csv")
    if uploaded_file is not None:
        upload_config(uploaded_file)

    # Display the current config
    st.write("Current PDF Config:")
    pdf_config = pd.read_csv(StringIO(data), index_col=0)
    st.dataframe(pdf_config)


if __name__ == "__main__":
    app()
