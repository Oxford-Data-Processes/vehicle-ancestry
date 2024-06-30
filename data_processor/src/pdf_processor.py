import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io
import pdfplumber
import numpy as np
import re
from data import config


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


import pdfplumber
import pandas as pd


def extract_pdf_text(pdf_path):
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        # Initialize an empty list to store the extracted data
        data = []
        # Iterate through each page
        for page_num, page in enumerate(pdf.pages):
            # Extract the text with bounding boxes
            for element in page.extract_words():
                text = element["text"]
                x0, y0, x1, y1 = (
                    element["x0"],
                    element["top"],
                    element["x1"],
                    element["bottom"],
                )
                data.append([page_num + 1, text, x0, y0, x1, y1])

        # Convert the list to a DataFrame
        df = pd.DataFrame(data, columns=["page", "text", "x0", "y0", "x1", "y1"])
        return df


def find_interval(number, intervals):
    intervals = sorted(intervals)
    for interval in intervals:
        if number >= interval[0] and number < interval[1]:
            return interval
    return None


def assign_intervals_and_values(df, gridlines):
    # Create a list of intervals from the gridlines
    intervals = [item["interval"] for item in gridlines]
    df["interval"] = df["x0"].apply(lambda x: find_interval(x, intervals))
    df["value"] = df["interval"].apply(
        lambda x: (
            next((item["label"] for item in gridlines if item["interval"] == x), None)
            if x
            else None
        )
    )
    return df


def process_consecutive_values(df, target_value):
    processed_rows = []
    current_row = None

    for _, row in df.iterrows():
        if row["value"] == target_value:
            if current_row is None:
                current_row = row.copy()
            else:
                # Concatenate the text field
                current_row["text"] += row["text"]
                # Update the bounding box
                current_row["x1"] = max(current_row["x1"], row["x1"])
                current_row["y1"] = max(current_row["y1"], row["y1"])
        else:
            if current_row is not None:
                processed_rows.append(current_row)
                current_row = None
            processed_rows.append(row)

    if current_row is not None:
        processed_rows.append(current_row)

    return pd.DataFrame(processed_rows)


def concatenate_values(df):
    new_value_column = []
    new_text_column = []

    # Iterate over the dataframe to concatenate values
    current_value = None
    current_text = ""

    for value, text in zip(df["value"], df["text"]):
        if value == current_value:
            current_text += text + " "
        else:
            if current_value is not None:
                new_value_column.append(current_value)
                new_text_column.append(current_text.strip())
            current_value = value
            current_text = text + " "  # Added space at the end of each text

    # Append the last accumulated values
    if current_value is not None:
        new_value_column.append(current_value)
        new_text_column.append(current_text.strip())

    # Create a new DataFrame with the concatenated values
    new_df = pd.DataFrame({"value": new_value_column, "text": new_text_column})
    return new_df


def transform_df(new_df, unique_identifier):
    new_df[unique_identifier] = new_df.apply(
        lambda x: x.text if x.value == unique_identifier else None, axis=1
    ).ffill()
    new_df = new_df.pivot_table(
        index=unique_identifier, columns="value", values="text", aggfunc="first"
    )
    new_df.reset_index(drop=True, inplace=True)
    new_df["vrm"] = new_df["vrm"].str.replace(" ", "")

    # Filter rows where "vrm" column matches the specified pattern
    new_df = new_df[
        new_df["vrm"].str.contains(r"^(?:[A-Z]+[0-9]|[0-9]+[A-Z])[A-Z0-9]*$", na=False)
    ]
    return new_df


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

        council = st.selectbox("Select Council:", tuple(sorted(config.keys())))

        gridlines = config[council]["gridlines"]
        unique_identifier = config[council]["unique_identifier"]
        pdf_path = f"pdfs/tabular/{council}.pdf"

        if st.button("Process PDF"):

            df = extract_pdf_text(pdf_path)
            st.write("Pre-processed Data")
            st.dataframe(df)

            df = assign_intervals_and_values(df, gridlines)
            df = process_consecutive_values(df, target_value=unique_identifier)
            df_reduced = df[["text", "value"]].reset_index(drop=True)
            new_df = concatenate_values(df_reduced)
            new_df = transform_df(new_df, unique_identifier)

            st.write("Processed Data")
            st.dataframe(new_df)

            if st.button("Confirm Upload"):
                st.success("Uploaded successfully!")
                # Reset the processed state so the message doesn't keep showing up
                st.session_state["processed"] = False

    else:
        st.write("Please upload a PDF file to process the data.")
