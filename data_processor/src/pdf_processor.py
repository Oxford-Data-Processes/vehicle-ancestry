import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io
import pdfplumber
import requests
from io import StringIO
import os
from typing import List, Dict, Tuple, Optional



def display_first_two_pdf_pages(pdf_bytes: bytes) -> None:
    """
    Display the first two pages of a PDF file.

    Args:
        pdf_bytes (bytes): The PDF file content in bytes.
    """
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


def extract_pdf_text(pdf_path: str) -> pd.DataFrame:
    """
    Extract text and bounding box information from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        pd.DataFrame: DataFrame containing extracted text and bounding box information.
    """
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


def find_interval(number: float, intervals: List[Tuple[float, float]]) -> Optional[Tuple[float, float]]:
    """
    Find the interval that contains a given number.

    Args:
        number (float): The number to find an interval for.
        intervals (List[Tuple[float, float]]): List of intervals to search.

    Returns:
        Optional[Tuple[float, float]]: The interval containing the number, or None if not found.
    """
    intervals = sorted(intervals)
    for interval in intervals:
        if number >= interval[0] and number < interval[1]:
            return interval
    return None


def assign_intervals_and_values(df: pd.DataFrame, gridlines: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Assign intervals and values to DataFrame based on gridlines.

    Args:
        df (pd.DataFrame): Input DataFrame.
        gridlines (List[Dict[str, Any]]): List of gridline dictionaries.

    Returns:
        pd.DataFrame: DataFrame with assigned intervals and values.
    """
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


def process_consecutive_values(df: pd.DataFrame, target_value: str) -> pd.DataFrame:
    """
    Process consecutive values in DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.
        target_value (str): Target value to process.

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    processed_rows = []
    current_row = None

    for _, row in df.iterrows():
        if row["value"] == target_value:
            if current_row is None:
                current_row = row.copy()
            else:
                # Concatenate the text field
                current_row["text"] += " " + row["text"]
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


def split_dataframe(df_reduced: pd.DataFrame, unique_identifier: str) -> List[pd.DataFrame]:
    """
    Split DataFrame into chunks based on unique identifier.

    Args:
        df_reduced (pd.DataFrame): Input DataFrame.
        unique_identifier (str): Unique identifier to split on.

    Returns:
        List[pd.DataFrame]: List of split DataFrames.
    """
    # Initialize an empty list to store the dataframes
    dataframes_list = []

    # Find the indices where "reference_number" appears in the value column
    reference_indices = df_reduced[df_reduced["value"] == unique_identifier].index

    # Iterate through the indices and create dataframes
    for i in range(len(reference_indices)):
        start_idx = reference_indices[i]
        end_idx = (
            reference_indices[i + 1]
            if i + 1 < len(reference_indices)
            else len(df_reduced)
        )
        chunk_df = df_reduced[start_idx:end_idx].reset_index(drop=True)
        dataframes_list.append(chunk_df)

    return dataframes_list


def process_dataframes(dataframes_list: List[pd.DataFrame], unique_identifier: str) -> pd.DataFrame:
    """
    Process list of DataFrames into a single DataFrame.

    Args:
        dataframes_list (List[pd.DataFrame]): List of DataFrames to process.
        unique_identifier (str): Unique identifier column.

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    new_dataframes_list = []

    for df in dataframes_list:
        df = df.groupby("value", as_index=False).agg({"text": " ".join})
        df[unique_identifier] = df[df["value"] == unique_identifier]["text"].iloc[0]
        df = df.pivot_table(
            index=unique_identifier, columns="value", values="text", aggfunc="first"
        )
        df.reset_index(inplace=True, drop=True)
        new_dataframes_list.append(df)

    new_df = pd.concat(new_dataframes_list)
    return new_df


def transform_df(new_df: pd.DataFrame, unique_identifier: str, date_format: Optional[str]) -> pd.DataFrame:
    """
    Transform DataFrame by applying various operations.

    Args:
        new_df (pd.DataFrame): Input DataFrame.
        unique_identifier (str): Unique identifier column.
        date_format (Optional[str]): Date format string.

    Returns:
        pd.DataFrame: Transformed DataFrame.
    """
    new_df["reg"] = new_df["reg"].str.replace(" ", "")

    # Filter rows where "reg" column matches the specified pattern
    new_df = new_df[
        new_df["reg"].str.contains(r"^(?:[A-Z]+[0-9]|[0-9]+[A-Z])[A-Z0-9]*$", na=False)
    ]
    if date_format is not None:
        if "date_from" in new_df.columns:
            new_df["date_from"] = pd.to_datetime(
                new_df["date_from"], format=date_format, errors="coerce"
            ).dt.strftime("%d/%m/%Y")
        if "date_to" in new_df.columns:
            new_df["date_to"] = pd.to_datetime(
                new_df["date_to"], format=date_format, errors="coerce"
            ).dt.strftime("%d/%m/%Y")

    # Remove rows where date format does not match
    if "date_from" in new_df.columns:
        new_df = new_df[new_df["date_from"].notna()]
    if "date_to" in new_df.columns:
        new_df = new_df[new_df["date_to"].notna()]

    # Select the required columns
    columns_to_select = ["reg", "make", "model", "date_from", "date_to"]
    existing_columns = [col for col in columns_to_select if col in new_df.columns]
    new_df = new_df[existing_columns]
    new_df = new_df.sort_values(by="reg", ascending=True)

    return new_df


def download_config(file_name: str) -> pd.DataFrame:
    """
    Download configuration file from S3 bucket.

    Args:
        file_name (str): Name of the file to download.

    Returns:
        pd.DataFrame: DataFrame containing the configuration data.
    """
    url = f"{AWS_PRESIGNED_URL}/{file_name}"
    response = requests.get(url, stream=True)
    response.raise_for_status()
    data = response.content.decode("utf-8")

    df = pd.read_csv(StringIO(data), index_col=0)
    return df


def app() -> None:
    """
    Main application function for PDF Processor.
    """
    pdf_config = download_config("pdf_config.csv").transpose().to_dict()

    # Title of the application
    st.title("PDF Processor")
    # File uploader allows user to add their own PDF
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()

        # Displaying the file
        st.write("Uploaded PDF file:")

        display_first_two_pdf_pages(bytes_data)

        council = st.selectbox("Select Council:", tuple(sorted(pdf_config.keys())))

        gridlines = eval(pdf_config[council]["gridlines"])
        unique_identifier = [item["label"] for item in gridlines][0]
        date_format = pdf_config[council]["date_format"]
        pdf_path = f"pdf_files/tabular/{council}.pdf"

        if st.button("Process PDF"):

            pdf_path = f"pdf_files/tabular/{council}.pdf"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            df = extract_pdf_text(pdf_path)
            st.write("Pre-processed Data")
            st.dataframe(df)

            st.write(pdf_config[council])

            df = assign_intervals_and_values(df, gridlines)
            df = process_consecutive_values(df, target_value=unique_identifier)
            df_reduced = df[["text", "value"]].reset_index(drop=True)
            dataframes_list = split_dataframe(df_reduced, unique_identifier)
            new_df = process_dataframes(dataframes_list, unique_identifier)
            new_df = transform_df(new_df, unique_identifier, date_format)

            if "reg" not in new_df.columns:
                st.error("Error: 'reg' column is missing from the processed data.")
                return

            st.success(
                "Validation passed: Required columns are present in the processed data."
            )

            st.write("Processed Data")
            st.dataframe(new_df)

            st.download_button(
                label="Download Processed Data",
                data=new_df.to_csv(index=False),
                file_name=f"{council}_{pd.Timestamp('now').strftime('%d_%m_%YT%H_%M_%S')}.csv",
                mime="text/csv",
            )

    else:
        st.write("Please upload a PDF file to process the data.")
