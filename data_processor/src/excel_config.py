import streamlit as st
import pandas as pd
import datetime


def download_config(file_path, label, file_name, mime):
    with open(file_path, "r") as file:
        data = file.read()
    st.download_button(
        label=label,
        data=data,
        file_name=file_name,
        mime=mime,
    )


def edit_config():
    st.write("Current Excel Column Mappings")
    df_mappings = pd.read_csv("data_processor/data/excel_mappings.csv")
    df_mappings.sort_values(by=["mapped_value", "raw_value"], inplace=True)
    st.dataframe(df_mappings)

    st.write("Add New Mapping")
    raw_value = st.text_input("Enter raw value:")
    mapped_value = st.text_input("Enter mapped value:")

    if st.button("Add Mapping"):
        new_mapping = pd.DataFrame(
            [[raw_value, mapped_value]], columns=["raw_value", "mapped_value"]
        )
        df_mappings = pd.concat([df_mappings, new_mapping], ignore_index=True)
        df_mappings.sort_values(by=["mapped_value", "raw_value"], inplace=True)
        st.dataframe(df_mappings)

        timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        file_path = f"data_processor/data/excel_mappings_{timestamp}.csv"
        df_mappings.to_csv(file_path, index=False)
        st.success(f"New mapping added and saved to {file_path}")


def app():
    st.title("Excel Config")
    download_config(
        "data_processor/data/excel_mappings.csv",
        "Download Excel Column Mappings",
        "excel_mappings.csv",
        "csv",
    )
    edit_config()


if __name__ == "__main__":
    app()
