import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io
import pdfplumber


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
    data = []
    header = None
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract table settings: Look for lines
            tables = page.extract_tables(
                {"vertical_strategy": "lines", "horizontal_strategy": "lines"}
            )

            for table in tables:
                # If header is not set and has_header is True, set header and skip the first row
                if has_header and header is None:
                    header = table[0] + ["page"]
                    start_row_index = 1
                    continue  # Skip the rest of the loop to avoid adding the header as data

                # If header is not set and has_header is False, create a default header
                if header is None:
                    header = [f"column_{i}" for i in range(len(table[0]))] + ["page"]
                    start_row_index = 0

                # Iterate over the table rows, starting from the appropriate index
                for row in table[start_row_index:]:
                    row_with_page = row + [page_num]
                    data.append(row_with_page)

    return header, data


def update_headers(column_mappings, df, council):
    column_map = column_mappings[council]
    # Rename the columns using the provided column mapping
    df.rename(columns=column_map, inplace=True)

    return df


def clean_dataframe(df, column_mappings, council):

    clean_headers = list(set(column_mappings[council].values()))

    has_null = df[clean_headers].isnull().values.any()
    if has_null:

        # Initialize a list to hold the cleaned data
        cleaned_data = []

        # Iterate over the DataFrame rows
        for index, row in df.iterrows():
            # Initialize a dictionary to hold the non-null values for the current row
            non_null_values = {header: None for header in clean_headers}

            # Iterate over each header and collect the last non-null value if available
            for header in clean_headers:

                # Get all the values from the columns that were mapped to the current header
                values = row[header].dropna().tolist()
                if values:  # If there are any non-null values
                    # Assign the last non-null value to the corresponding header in the dictionary
                    non_null_values[header] = values[-1]

            # Append the dictionary with non-null values to the cleaned data list
            cleaned_data.append(non_null_values)

        # Create a new DataFrame using the cleaned data
        cleaned_df = pd.DataFrame(cleaned_data, columns=clean_headers)

        return cleaned_df

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
        number, has_header = council_mappings[council]

        if st.button("Process PDF"):
            column_mappings = {
                "Salford": {"REG": "vrm", "VEHICLE TYPE": "make"},
                "Renfrewshire": {"column_1": "vrm", "column_2": "make"},
                "East Lothian": {
                    "column_0": "vrm",
                    "column_1": "vrm",
                    "column_3": "make",
                    "column_4": "make",
                    "column_6": "model",
                    "column_7": "model",
                },
            }
            header, table_data = extract_table_from_pdf(
                uploaded_file, has_header=has_header
            )
            df = pd.DataFrame(table_data, columns=header)
            df = update_headers(column_mappings, df, council)
            df_clean = clean_dataframe(df, column_mappings, council)

            st.write("Processed Data")
            st.dataframe(df_clean)

            if st.button("Confirm Upload"):
                st.success("Uploaded successfully!")
                # Reset the processed state so the message doesn't keep showing up
                st.session_state["processed"] = False

    else:
        st.write("Please upload a PDF file to process the data.")
