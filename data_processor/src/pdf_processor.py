import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io
import pdfplumber
import numpy as np
import re

config = {
    "Bedford": {
        "gridlines": [
            {"interval": (52, 121), "label": "plate"},
            {"interval": (121, 220), "label": "vrm"},
            {"interval": (220, 312), "label": "make"},
            {"interval": (312, 418), "label": "model"},
            {"interval": (418, 482), "label": "licence_start"},
            {"interval": (482, 538), "label": "licence_end"},
        ],
        "unique_identifier": "plate",
    },
    "Pembrokeshire": {
        "gridlines": [
            {"interval": (76, 158), "label": "vrm"},
            {"interval": (158, 274), "label": "make"},
            {"interval": (274, 418), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Calderdale": {
        "gridlines": [
            {"interval": (100, 220), "label": "vrm"},
            {"interval": (220, 340), "label": "make"},
            {"interval": (340, 460), "label": "model"},
            {"interval": (580, 712), "label": "licence_start"},
            {"interval": (712, 800), "label": "licence_end"},
        ],
        "unique_identifier": "vrm",
    },
    "BCP": {
        "gridlines": [
            {"interval": (42, 76), "label": "reference_number"},
            {"interval": (76, 212), "label": "name"},
            {"interval": (212, 268), "label": "vrm"},
            {"interval": (268, 311), "label": "licence_number"},
            {"interval": (311, 364), "label": "licence_start"},
            {"interval": (364, 412), "label": "licence_end"},
            {"interval": (412, 528), "label": "make"},
            {"interval": (528, 590), "label": "licence_type"},
        ],
        "unique_identifier": "reference_number",
    },
    "Cheshire West": {
        "gridlines": [
            {"interval": (52, 160), "label": "make"},
            {"interval": (160, 478), "label": "model"},
            {"interval": (478, 540), "label": "vrm"},
        ],
        "unique_identifier": "vrm",
    },
    "East Northamptonshire": {
        "gridlines": [
            {"interval": (55, 130), "label": "vrm"},
            {"interval": (160, 240), "label": "make"},
            {"interval": (240, 540), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Fylde": {
        "gridlines": [
            {"interval": (18, 87), "label": "vrm"},
            {"interval": (87, 216), "label": "make"},
            {"interval": (216, 340), "label": "model"},
            {"interval": (340, 460), "label": "licence_start"},
            {"interval": (460, 540), "label": "licence_end"},
        ],
        "unique_identifier": "vrm",
    },
    "Great Yarmouth": {
        "gridlines": [
            {"interval": (52, 160), "label": "vrm"},
            {"interval": (160, 238), "label": "make"},
            {"interval": (238, 540), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Horsham": {
        "gridlines": [
            {"interval": (52, 103), "label": "reference_number"},
            {"interval": (103, 152), "label": "licence_type"},
            {"interval": (152, 218), "label": "name"},
            {"interval": (218, 266), "label": "vrm"},
            {"interval": (266, 320), "label": "make"},
            {"interval": (320, 386), "label": "model"},
            {"interval": (386, 446), "label": "licence_start"},
            {"interval": (446, 484), "label": "licence_end"},
            {"interval": (484, 540), "label": "plate"},
        ],
        "unique_identifier": "vrm",
    },
    "Kettering": {
        "gridlines": [
            {"interval": (55, 102), "label": "vrm"},
            {"interval": (148, 214), "label": "make"},
            {"interval": (214, 540), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Maldon": {
        "gridlines": [
            {"interval": (35, 142), "label": "plate"},
            {"interval": (142, 258), "label": "vrm"},
            {"interval": (258, 312), "label": "make"},
            {"interval": (312, 445), "label": "model"},
            {"interval": (445, 576), "label": "colour"},
            {"interval": (576, 648), "label": "seats"},
            {"interval": (648, 736), "label": "licence_start"},
            {"interval": (736, 800), "label": "licence_end"},
        ],
        "unique_identifier": "vrm",
    },
    "Milton Keynes": {
        "gridlines": [
            {"interval": (256, 288), "label": "plate"},
            {"interval": (288, 336), "label": "vrm"},
            {"interval": (336, 406), "label": "make"},
            {"interval": (406, 488), "label": "model"},
            {"interval": (488, 742), "label": "name"},
            {"interval": (742, 800), "label": "licence_end"},
        ],
        "unique_identifier": "plate",
    },
    "North Lanarkshire": {
        "gridlines": [
            {"interval": (52, 140), "label": "vrm"},
            {"interval": (140, 210), "label": "make"},
            {"interval": (210, 360), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Powys": {
        "gridlines": [
            {"interval": (3, 38), "label": "plate"},
            {"interval": (98, 222), "label": "vrm"},
            {"interval": (222, 312), "label": "make"},
            {"interval": (312, 404), "label": "model"},
            {"interval": (404, 482), "label": "licence_start"},
        ],
        "unique_identifier": "plate",
    },
    "Swansea": {
        "gridlines": [
            {"interval": (52, 130), "label": "vrm"},
            {"interval": (130, 240), "label": "make"},
        ],
        "unique_identifier": "vrm",
    },
    "Wealden": {
        "gridlines": [
            {"interval": (56, 98), "label": "plate"},
            {"interval": (98, 136), "label": "vrm"},
            {"interval": (136, 206), "label": "make"},
            {"interval": (206, 272), "label": "model"},
            {"interval": (272, 315), "label": "colour"},
            {"interval": (315, 404), "label": "name"},
            {"interval": (450, 488), "label": "licence_start"},
            {"interval": (496, 540), "label": "licence_end"},
        ],
        "unique_identifier": "vrm",
    },
    "West Lothian": {
        "gridlines": [
            {"interval": (52, 184), "label": "licence_type"},
            {"interval": (184, 295), "label": "vrm"},
            {"interval": (295, 372), "label": "make"},
            {"interval": (372, 440), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "West Morland Barrow": {
        "gridlines": [
            {"interval": (55, 118), "label": "vrm"},
            {"interval": (118, 200), "label": "make"},
            {"interval": (200, 300), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Argyll and Bute": {
        "gridlines": [
            {"interval": (52, 158), "label": "vrm"},
            {"interval": (158, 245), "label": "make"},
            {"interval": (245, 400), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "East Lothian": {
        "gridlines": [
            {"interval": (76, 168), "label": "vrm"},
            {"interval": (168, 270), "label": "make"},
            {"interval": (270, 418), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Renfrewshire": {
        "gridlines": [
            {"interval": (52, 138), "label": "reference_number"},
            {"interval": (138, 248), "label": "vrm"},
            {"interval": (248, 440), "label": "make"},
        ],
        "unique_identifier": "vrm",
    },
    "Salford": {
        "gridlines": [
            {"interval": (28, 78), "label": "reference_number"},
            {"interval": (78, 136), "label": "licence_type"},
            {"interval": (136, 198), "label": "licence_start"},
            {"interval": (198, 250), "label": "licence_end"},
            {"interval": (286, 392), "label": "make"},
            {"interval": (392, 450), "label": "vrm"},
        ],
        "unique_identifier": "reference_number",
    },
    "Corby": {
        "gridlines": [
            {"interval": (248, 312), "label": "plate"},
            {"interval": (312, 390), "label": "licence_start"},
            {"interval": (390, 460), "label": "vrm"},
            {"interval": (460, 538), "label": "make"},
            {"interval": (538, 600), "label": "model"},
        ],
        "unique_identifier": "plate",
    },
    "Cornwall": {
        "gridlines": [
            {"interval": (28, 121), "label": "reference_number"},
            {"interval": (208, 318), "label": "vrm"},
            {"interval": (318, 416), "label": "make"},
            {"interval": (416, 570), "label": "model"},
            {"interval": (618, 700), "label": "licence_end"},
        ],
        "unique_identifier": "reference_number",
    },
    "Derby": {
        "gridlines": [
            {"interval": (32, 88), "label": "plate"},
            {"interval": (88, 320), "label": "name"},
            {"interval": (320, 416), "label": "vrm"},
            {"interval": (416, 540), "label": "make"},
        ],
        "unique_identifier": "plate",
    },
    "East Dunbarton": {
        "gridlines": [
            {"interval": (76, 150), "label": "vrm"},
            {"interval": (150, 240), "label": "make"},
            {"interval": (240, 400), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Eastleigh": {
        "gridlines": [
            {"interval": (56, 196), "label": "vrm"},
            {"interval": (196, 276), "label": "make"},
            {"interval": (276, 400), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Anglesey": {
        "gridlines": [
            {"interval": (78, 112), "label": "licence_type"},
            {"interval": (112, 368), "label": "vrm"},
            {"interval": (368, 514), "label": "make"},
            {"interval": (514, 750), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Perth Kinross": {
        "gridlines": [
            {"interval": (76, 196), "label": "vrm"},
            {"interval": (196, 286), "label": "make"},
            {"interval": (286, 400), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "Rother": {
        "gridlines": [
            {"interval": (50, 96), "label": "plate"},
            {"interval": (96, 148), "label": "vrm"},
            {"interval": (148, 212), "label": "make"},
            {"interval": (212, 268), "label": "model"},
            {"interval": (456, 499), "label": "licence_start"},
            {"interval": (499, 560), "label": "licence_end"},
        ],
        "unique_identifier": "plate",
    },
    "Stockton": {
        "gridlines": [
            {"interval": (40, 230), "label": "licence_type"},
            {"interval": (276, 386), "label": "vrm"},
            {"interval": (386, 510), "label": "make"},
            {"interval": (510, 578), "label": "licence_start"},
            {"interval": (578, 644), "label": "licence_end"},
        ],
        "unique_identifier": "vrm",
    },
    "Stroud": {
        "gridlines": [
            {"interval": (50, 128), "label": "vrm"},
            {"interval": (128, 206), "label": "make"},
            {"interval": (206, 340), "label": "model"},
            {"interval": (340, 420), "label": "licence_start"},
            {"interval": (420, 540), "label": "licence_end"},
        ],
        "unique_identifier": "vrm",
    },
    "Wellingborough": {
        "gridlines": [
            {"interval": (50, 128), "label": "vrm"},
            {"interval": (128, 206), "label": "make"},
            {"interval": (206, 340), "label": "model"},
        ],
        "unique_identifier": "vrm",
    },
    "West Lancashire": {
        "gridlines": [
            {"interval": (20, 50), "label": "plate"},
            {"interval": (50, 116), "label": "vrm"},
            {"interval": (116, 286), "label": "licence_type"},
            {"interval": (286, 360), "label": "make"},
            {"interval": (360, 510), "label": "model"},
            {"interval": (703, 760), "label": "licence_start"},
            {"interval": (760, 826), "label": "licence_end"},
        ],
        "unique_identifier": "plate",
    },
    "Wigan": {
        "gridlines": [
            {"interval": (76, 200), "label": "licence_type"},
            {"interval": (200, 324), "label": "plate"},
            {"interval": (324, 436), "label": "vrm"},
            {"interval": (436, 538), "label": "make"},
            {"interval": (538, 654), "label": "model"},
            {"interval": (1110, 1200), "label": "licence_end"},
        ],
        "unique_identifier": "plate",
    },
    "Wiltshire": {
        "gridlines": [
            {"interval": (2, 82), "label": "plate"},
            {"interval": (128, 188), "label": "make"},
            {"interval": (188, 272), "label": "model"},
            {"interval": (272, 356), "label": "vrm"},
            {"interval": (356, 428), "label": "licence_start"},
            {"interval": (428, 540), "label": "licence_end"},
        ],
        "unique_identifier": "plate",
    },
}


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
