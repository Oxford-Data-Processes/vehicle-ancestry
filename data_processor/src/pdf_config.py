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
    with open("data_processor/data/pdf_config.json", "r") as file:
        pdf_config = json.load(file)

    council = st.selectbox(
        "Select Council:", list(pdf_config.keys()) + ["Add New Council"]
    )

    if council == "Add New Council":
        new_council = st.text_input("Enter new Council name:")
        new_config = st.text_area(
            "Enter new config in JSON format:",
            value='[{"interval": [52, 158], "label": "reg"}, {"interval": [158, 245], "label": "make"}, {"interval": [245, 400], "label": "model"}]',
        )

        if st.button("Add Council"):
            try:
                new_config = json.loads(new_config)
                pdf_config[new_council] = {"gridlines": new_config}

                with open(
                    f"data_processor/data/pdf_config_{pd.Timestamp('now').strftime('%d_%m_%YT%H_%M_%S')}.json",
                    "w",
                ) as file:
                    json.dump(pdf_config, file)

                st.success("New Council added successfully.")
            except json.JSONDecodeError:
                st.error("Invalid JSON format for new config.")
    elif council:
        st.write("Current Config for", council)
        st.json(pdf_config[council])

        new_gridlines = st.text_area(
            "Enter new gridlines in JSON format:",
            value=json.dumps(pdf_config[council]["gridlines"]),
        )

        if st.button("Save Changes"):
            try:
                new_gridlines = json.loads(new_gridlines)
                pdf_config[council]["gridlines"] = new_gridlines

                with open(
                    f"data_processor/data/pdf_config_{pd.Timestamp('now').strftime('%d_%m_%YT%H_%M_%S')}.json",
                    "w",
                ) as file:
                    json.dump(pdf_config, file)

                st.success("Changes saved successfully.")
            except json.JSONDecodeError:
                st.error("Invalid JSON format for gridlines.")


def app():
    st.title("PDF Config")
    download_config(
        "data_processor/data/pdf_config.json",
        "Download PDF Config",
        "pdf_config.json",
        "application/json",
    )
    edit_config()


if __name__ == "__main__":
    app()
