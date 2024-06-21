import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io
import pdfplumber
import numpy as np
import re


def display_first_two_pdf_pages(pdf_bytes):
    # Load the PDF file from bytes
    pdf = fitz.open("pdf", pdf_bytes)
    num_pages = len(pdf)

    # Create a two-column layout if there are at least two pages, otherwise one column
    if num_pages >= 2:
        cols = st.columns(2)
    else:
        cols = st.columns(1)

    # Display the first page
    page = pdf.load_page(0)
    pix = page.get_pixmap()
    img_data = pix.tobytes("ppm")
    image = io.BytesIO(img_data)
    with cols[0]:
        st.image(image, caption="First page of the PDF", use_column_width=True)

    # Display the second page if it exists
    if num_pages >= 2:
        page = pdf.load_page(1)
        pix = page.get_pixmap()
        img_data = pix.tobytes("ppm")
        image = io.BytesIO(img_data)
        with cols[1]:
            st.image(image, caption="Second page of the PDF", use_column_width=True)

    # Close the PDF file
    pdf.close()


def extract_table_from_pdf(pdf_path, has_header):
    dataframe_list = []
    header = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables(
                {"vertical_strategy": "lines", "horizontal_strategy": "lines"}
            )

            for table_index, table in enumerate(tables):
                if has_header:
                    if len(table) > 1:  # Ensure there is at least one row of data
                        header = table[0] + ["page"]
                        for row in table[1:]:
                            if len(row) < len(header) - 1:
                                row.extend([None] * (len(header) - 1 - len(row)))
                            elif len(row) > len(header) - 1:
                                row = row[: len(header) - 1]
                            row.append(page_num)
                        df = pd.DataFrame(table[1:], columns=header)
                        dataframe_list.append(df)
                else:
                    header = [f"column_{i}" for i in range(len(table[0]))] + ["page"]
                    for row in table:
                        if len(row) < len(header) - 1:
                            row.extend([None] * (len(header) - 1 - len(row)))
                        elif len(row) > len(header) - 1:
                            row = row[: len(header) - 1]
                        row.append(page_num)
                    df = pd.DataFrame(table, columns=header)
                    dataframe_list.append(df)

    if dataframe_list:
        try:
            df_extracted = pd.concat(dataframe_list)
            df_extracted = df_extracted.replace("", None)
            return df_extracted
        except AssertionError as e:
            return pd.DataFrame()
    else:
        return (
            pd.DataFrame()
        )  # Return an empty DataFrame if no tables were extracted or matched


def update_headers(column_mappings, df, council):
    column_map = column_mappings[council]
    # Rename the columns using the provided column mapping
    df.rename(columns=column_map, inplace=True)

    return df


def clean_dataframe(df):
    if "vrm.1" in df.columns:
        df["vrm"] = np.where(df["vrm"].isnull(), df["vrm.1"], df["vrm"])
        df["vrm"] = df["vrm"].fillna(method="ffill")
        df.drop(columns=["vrm.1"], inplace=True)
        df.drop_duplicates(inplace=True, subset=["vrm"])
        df.reset_index(inplace=True, drop=True)

    for column in ["make", "model"]:
        if f"{column}.1" in df.columns:
            df[column] = df[column].combine_first(df[f"{column}.1"])
            df.drop(columns=[f"{column}.1"], inplace=True)

    if "vrm" in df.columns:
        df = df.copy()[
            df["vrm"].apply(lambda x: re.match(r"^[A-Z0-9\s]*$", str(x)) is not None)
        ]

    return df


def app():

    # Title of the application
    st.title("PDF Uploader")

    # File uploader allows user to add their own PDF
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()

        # Displaying the file
        st.write("Uploaded PDF file:")

        display_first_two_pdf_pages(bytes_data)

        council = st.selectbox(
            "Select Council:",
            (
                "East Lothian",
                "Renfrewshire",
                "Salford",
            ),
        )
        council_mappings = {
            "Salford": (1, True),
            "Renfrewshire": (2, False),
            "East Lothian": (3, False),
        }
        _, has_header = council_mappings[council]

        if st.button("Process PDF"):
            column_mappings = {
                "Salford": {"REG": "vrm", "VEHICLE TYPE": "make"},
                "Renfrewshire": {"column_1": "vrm", "column_2": "make"},
                "East Lothian": {
                    "column_0": "vrm",
                    "column_1": "vrm.1",
                    "column_3": "make",
                    "column_4": "make.1",
                    "column_6": "model",
                    "column_7": "model.1",
                },
            }
            df = extract_table_from_pdf(uploaded_file, has_header=has_header)
            df = update_headers(column_mappings, df, council)
            df_clean = clean_dataframe(df)

            st.write("Processed Data")
            st.dataframe(df_clean)

            if st.button("Confirm Upload"):
                st.success("Uploaded successfully!")
                # Reset the processed state so the message doesn't keep showing up
                st.session_state["processed"] = False

    else:
        st.write("Please upload a PDF file to process the data.")
