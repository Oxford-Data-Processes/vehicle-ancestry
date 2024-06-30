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
    df["interval"] = df["x0"].apply(lambda x: find_interval(x, list(gridlines.keys())))
    df["value"] = df["interval"].apply(lambda x: gridlines.get(x, None) if x else None)
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

        config = {
            "Bedford": {
                "gridlines": {
                    (52, 121): "plate",
                    (121, 220): "vrm",
                    (220, 312): "make",
                    (312, 418): "model",
                    (418, 482): "licence_start",
                    (482, 538): "licence_end",
                },
                "unique_identifier": "plate",
            },
            "BCP": {
                "gridlines": {
                    (42, 76): "reference_number",
                    (76, 212): "name",
                    (212, 268): "vrm",
                    (268, 311): "licence_number",
                    (311, 364): "licence_start",
                    (364, 412): "licence_end",
                    (412, 528): "make",
                    (528, 590): "licence_type",
                },
                "unique_identifier": "reference_number",
            },
            "Cheshire West": {
                "gridlines": {
                    (52, 160): "make",
                    (160, 478): "model",
                    (478, 540): "vrm",
                },
                "unique_identifier": "vrm",
            },
            "East Northamptonshire": {
                "gridlines": {
                    (55, 130): "vrm",
                    (160, 240): "make",
                    (240, 540): "model",
                },
                "unique_identifier": "vrm",
            },
            "Fylde": {
                "gridlines": {
                    (18, 87): "vrm",
                    (87, 216): "make",
                    (216, 340): "model",
                    (340, 460): "licence_start",
                    (460, 540): "licence_end",
                },
                "unique_identifier": "vrm",
            },
            "Great Yarmouth": {
                "gridlines": {
                    (52, 160): "vrm",
                    (160, 238): "make",
                    (238, 540): "model",
                },
                "unique_identifier": "vrm",
            },
            "Horsham": {
                "gridlines": {
                    (52, 103): "reference_number",
                    (103, 152): "licence_type",
                    (152, 218): "name",
                    (218, 266): "vrm",
                    (266, 320): "make",
                    (320, 386): "model",
                    (386, 446): "licence_start",
                    (446, 484): "licence_end",
                    (484, 540): "plate",
                },
                "unique_identifier": "vrm",
            },
            "Kettering": {
                "gridlines": {
                    (55, 102): "vrm",
                    (148, 214): "make",
                    (214, 540): "model",
                },
                "unique_identifier": "vrm",
            },
            "Maldon": {
                "gridlines": {
                    (35, 142): "plate",
                    (142, 258): "vrm",
                    (258, 312): "make",
                    (312, 445): "model",
                    (445, 576): "colour",
                    (576, 648): "seats",
                    (648, 736): "licence_start",
                    (736, 800): "licence_end",
                },
                "unique_identifier": "vrm",
            },
            "Milton Keynes": {
                "gridlines": {
                    (256, 288): "plate",
                    (288, 336): "vrm",
                    (336, 406): "make",
                    (406, 488): "model",
                    (488, 742): "name",
                    (742, 800): "licence_end",
                },
                "unique_identifier": "plate",
            },
            "North Lanarkshire": {
                "gridlines": {
                    (52, 140): "vrm",
                    (140, 210): "make",
                    (210, 360): "model",
                },
                "unique_identifier": "vrm",
            },
            "Powys": {
                "gridlines": {
                    (3, 38): "plate",
                    (98, 222): "vrm",
                    (222, 312): "make",
                    (312, 404): "model",
                    (404, 482): "licence_start",
                },
                "unique_identifier": "plate",
            },
            "Swansea": {
                "gridlines": {(52, 130): "vrm", (130, 240): "make"},
                "unique_identifier": "vrm",
            },
            "Wealden": {
                "gridlines": {
                    (56, 98): "plate",
                    (98, 136): "vrm",
                    (136, 206): "make",
                    (206, 272): "model",
                    (272, 315): "colour",
                    (315, 404): "name",
                    (450, 488): "licence_start",
                    (496, 540): "licence_end",
                },
                "unique_identifier": "vrm",
            },
            "West Lothian": {
                "gridlines": {
                    (52, 184): "licence_type",
                    (184, 295): "vrm",
                    (295, 372): "make",
                    (372, 440): "model",
                },
                "unique_identifier": "vrm",
            },
            "West Morland Barrow": {
                "gridlines": {
                    (55, 118): "vrm",
                    (118, 200): "make",
                    (200, 300): "model",
                },
                "unique_identifier": "vrm",
            },
            "Argyll and Bute": {
                "gridlines": {
                    (52, 158): "vrm",
                    (158, 245): "make",
                    (245, 400): "model",
                },
                "unique_identifier": "vrm",
            },
            "East Lothian": {
                "gridlines": {
                    (77, 170): "vrm",
                    (220, 312): "make",
                    (312, 418): "model",
                },
                "unique_identifier": "vrm",
            },
            "Renfrewshire": {
                "gridlines": {
                    (52, 138): "reference_number",
                    (138, 248): "vrm",
                    (248, 440): "make",
                },
                "unique_identifier": "vrm",
            },
            "Salford": {
                "gridlines": {
                    (28, 78): "reference_number",
                    (78, 136): "licence_type",
                    (136, 198): "licence_start",
                    (198, 250): "licence_end",
                    (286, 392): "make",
                    (392, 450): "vrm",
                },
                "unique_identifier": "reference_number",
            },
            "Corby": {
                "gridlines": {
                    (248, 312): "plate",
                    (312, 390): "licence_start",
                    (390, 460): "vrm",
                    (460, 538): "make",
                    (538, 600): "model",
                },
                "unique_identifier": "plate",
            },
            "Cornwall": {
                "gridlines": {
                    (28, 121): "reference_number",
                    (208, 318): "vrm",
                    (318, 416): "make",
                    (416, 570): "model",
                    (618, 700): "licence_end",
                },
                "unique_identifier": "reference_number",
            },
            "Derby": {
                "gridlines": {
                    (32, 88): "plate",
                    (88, 320): "name",
                    (320, 416): "vrm",
                    (416, 540): "make",
                },
                "unique_identifier": "plate",
            },
            "East Dunbarton": {
                "gridlines": {
                    (76, 150): "vrm",
                    (150, 240): "make",
                    (240, 400): "model",
                },
                "unique_identifier": "vrm",
            },
            "Eastleigh": {
                "gridlines": {
                    (56, 196): "vrm",
                    (196, 276): "make",
                    (276, 400): "model",
                },
                "unique_identifier": "vrm",
            },
            "Anglesey": {
                "gridlines": {
                    (78, 112): "licence_type",
                    (112, 368): "vrm",
                    (368, 514): "make",
                    (514, 750): "model",
                },
                "unique_identifier": "vrm",
            },
            "Perth Kinross": {
                "gridlines": {
                    (76, 196): "vrm",
                    (196, 286): "make",
                    (286, 400): "model",
                },
                "unique_identifier": "vrm",
            },
            "Rother": {
                "gridlines": {
                    (50, 96): "plate",
                    (96, 148): "vrm",
                    (148, 212): "make",
                    (212, 268): "model",
                    (456, 499): "licence_start",
                    (499, 560): "licence_end",
                },
                "unique_identifier": "plate",
            },
            "Stockton": {
                "gridlines": {
                    (40, 230): "licence_type",
                    (276, 386): "vrm",
                    (386, 510): "make",
                    (510, 578): "licence_start",
                    (578, 644): "licence_end",
                },
                "unique_identifier": "vrm",
            },
            "Stroud": {
                "gridlines": {
                    (50, 128): "vrm",
                    (128, 206): "make",
                    (206, 340): "model",
                    (340, 420): "licence_start",
                    (420, 540): "licence_end",
                },
                "unique_identifier": "vrm",
            },
            "Wellingborough": {
                "gridlines": {
                    (50, 128): "vrm",
                    (128, 206): "make",
                    (206, 340): "model",
                },
                "unique_identifier": "vrm",
            },
            "West Lancashire": {
                "gridlines": {
                    (20, 50): "plate",
                    (50, 116): "vrm",
                    (116, 286): "licence_type",
                    (286, 360): "make",
                    (360, 510): "model",
                    (703, 760): "licence_start",
                    (760, 826): "licence_end",
                },
                "unique_identifier": "plate",
            },
            "Wigan": {
                "gridlines": {
                    (76, 200): "licence_type",
                    (200, 324): "plate",
                    (324, 436): "vrm",
                    (436, 538): "make",
                    (538, 654): "model",
                    (1110, 1200): "licence_end",
                },
                "unique_identifier": "plate",
            },
            "Wiltshire": {
                "gridlines": {
                    (2, 82): "plate",
                    (128, 188): "make",
                    (188, 272): "model",
                    (272, 356): "vrm",
                    (356, 428): "licence_start",
                    (428, 540): "licence_end",
                },
                "unique_identifier": "plate",
            },
        }
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
