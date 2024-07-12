import streamlit as st
import pandas as pd
import datetime


def download_config(file_path, label, file_name, mime):
    with open(file_path, "r") as file:
        data = file.read()
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
        with open("data_processor/data/excel_mappings.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Config file uploaded successfully!")


def app():
    st.title("Excel Config")

    # Download the current config
    download_config(
        "data_processor/data/excel_mappings.csv",
        "Download Excel Column Mappings",
        "excel_mappings.csv",
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
