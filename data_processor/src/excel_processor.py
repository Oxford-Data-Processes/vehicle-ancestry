import streamlit as st
import pandas as pd
import json


def app():
    with open("data_processor/data/excel_config.json", "r") as file:
        excel_config = json.load(file)
    # Title of the application
    st.title("Excel File Uploader")

    # File uploader allows user to add their own Excel file
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    council = st.selectbox("Select Council", excel_config.keys())

    process_data = st.button("Process Data")

    if process_data:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()

        df = pd.read_excel(
            bytes_data, header=None if not excel_config[council]["has_headers"] else 0
        )
        st.write("Uploaded Excel file:")
        st.dataframe(df)
        if not excel_config[council]["has_headers"]:
            df.columns = list(excel_config[council]["column_mappings"].values())
        else:
            df.columns = df.columns.str.strip()
            df.rename(columns=excel_config[council]["column_mappings"], inplace=True)

        st.write(excel_config[council]["column_mappings"])
        df["vrm"] = df["vrm"].str.replace(" ", "")
        df = df.copy()[excel_config[council]["column_mappings"].values()]

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
