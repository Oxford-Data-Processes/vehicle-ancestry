import streamlit as st
import json
import pandas as pd


def download_config(file_path, label, file_name, mime):
    st.download_button(
        label=label,
        data=open(file_path, "r").read(),
        file_name=file_name,
        mime=mime,
    )


def edit_config():
    with open("data_processor/data/excel_config.json", "r") as file:
        excel_config = json.load(file)

    council = st.selectbox("Select Council:", list(excel_config.keys()))

    if council:
        st.write("Current Config for", council)
        st.json(excel_config[council])

        column_mappings = st.text_area(
            "Enter new column_mappings in JSON format:",
            value=json.dumps(excel_config[council]["column_mappings"]),
        )
        has_headers = st.text_input(
            "Enter new boolean has_headers value (true/false):",
            value=excel_config[council]["has_headers"],
        )

        if st.button("Save Changes"):
            try:
                column_mappings = json.loads(column_mappings)
                excel_config[council]["column_mappings"] = column_mappings
                excel_config[council]["has_headers"] = has_headers

                with open(
                    f"data_processor/data/excel_config_{pd.Timestamp('now').strftime('%d_%m_%YT%_%M_%S')}.json",
                    "w",
                ) as file:
                    json.dump(excel_config, file)

                st.success("Changes saved successfully.")
            except json.JSONDecodeError:
                st.error("Invalid JSON format for gridlines.")


def app():
    st.title("Excel Config")
    download_config(
        "data_processor/data/excel_config.json",
        "Download Excel Config",
        "excel_config.json",
        "application/json",
    )
    edit_config()


if __name__ == "__main__":
    app()
