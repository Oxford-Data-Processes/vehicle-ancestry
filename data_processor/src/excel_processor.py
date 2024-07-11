import streamlit as st
import pandas as pd
import json


def app():
    df_mappings = pd.read_csv("data_processor/data/excel_mappings.csv")

    with open("data_processor/data/excel_config.json", "r") as f:
        excel_config = json.load(f)

    # Title of the application
    st.title("Excel Processor")

    # File uploader allows user to add their own Excel file
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    council = st.selectbox("Select Council:", excel_config.keys())
    process_data = st.button("Process Data")

    if process_data:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()

        date_format = excel_config[council]["date_format"]

        df = pd.read_excel(
            bytes_data,
            sheet_name=0,
            parse_dates=True,
            date_parser=lambda x: (
                pd.to_datetime(x, format=date_format, errors="coerce")
                if date_format
                else None
            ),
        )
        df.columns = [
            col.replace(" ", "_").replace(":", "").strip().lower() for col in df.columns
        ]
        st.write("Uploaded Excel file:")
        st.dataframe(df)

        # Create a dictionary for renaming columns
        rename_dict = dict(zip(df_mappings["raw_value"], df_mappings["mapped_value"]))
        df.rename(columns=rename_dict, inplace=True)

        if "date_from" in df.columns:
            df["date_from"] = pd.to_datetime(
                df["date_from"], errors="coerce"
            ).dt.strftime("%d/%m/%Y")
        if "date_to" in df.columns:
            df["date_to"] = pd.to_datetime(df["date_to"], errors="coerce").dt.strftime(
                "%d/%m/%Y"
            )

        final_columns = ["reg", "make", "model", "date_from", "date_to"]
        existing_columns = [col for col in final_columns if col in df.columns]
        df = df[existing_columns]

        st.write("Processed Excel file:")
        st.dataframe(df)

        st.download_button(
            label="Download Processed Data",
            data=df.to_csv(index=False),
            file_name=f"{council}_{pd.Timestamp('now').strftime('%d_%m_%YT%H_%M_%S')}.csv",
            mime="text/csv",
        )

    else:
        pass


if __name__ == "__main__":
    app()
