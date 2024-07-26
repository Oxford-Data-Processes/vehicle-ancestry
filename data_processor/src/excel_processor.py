import streamlit as st
import pandas as pd
import requests
from io import StringIO


def download_config(file_name):

    url = f"https://vehicle-ancestry-bucket-654654324108.s3.amazonaws.com/{file_name}"
    response = requests.get(url, stream=True)
    response.raise_for_status()
    data = response.content.decode("utf-8")

    df = pd.read_csv(StringIO(data))
    return df


def app():
    df_mappings = download_config("excel_mappings.csv")

    # Title of the application
    st.title("Excel Processor")

    # File uploader allows user to add their own Excel file
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    process_data = st.button("Process Data")

    if process_data:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        df = pd.read_excel(bytes_data, sheet_name=0, parse_dates=True)
        df.columns = [
            col.replace(" ", "_").replace(":", "").strip().lower() for col in df.columns
        ]

        # Convert date columns to string format to preserve original formatting
        date_columns = df.select_dtypes(include=["datetime64"]).columns
        for col in date_columns:
            df[col] = df[col].dt.strftime("%d/%m/%Y")

        st.write("Uploaded Excel file:")
        st.dataframe(df)

        # Create a dictionary for renaming columns
        rename_dict = dict(zip(df_mappings["raw_value"], df_mappings["mapped_value"]))
        df.rename(columns=rename_dict, inplace=True)

        final_columns = ["reg", "make", "model", "date_from", "date_to"]
        existing_columns = [col for col in final_columns if col in df.columns]
        df = df[existing_columns]

        # Check if at least one date column and reg are included in the df
        required_columns = ["reg"]
        date_columns = ["date_from", "date_to"]

        if "reg" not in df.columns:
            st.error("Error: 'reg' column is missing from the processed data.")
            return

        if not any(col in df.columns for col in date_columns):
            st.error(
                "Error: At least one date column ('date_from' or 'date_to') is missing from the processed data."
            )
            return

        st.success(
            "Validation passed: Required columns are present in the processed data."
        )

        st.write("Processed Excel file:")
        st.dataframe(df)

        st.download_button(
            label="Download Processed Data",
            data=df.to_csv(index=False),
            file_name=f"{uploaded_file.name.split('.')[0]}_{pd.Timestamp('now').strftime('%d_%m_%YT%H_%M_%S')}.csv",
            mime="text/csv",
        )

    else:
        pass


if __name__ == "__main__":
    app()
