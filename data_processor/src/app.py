import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io

# Title of the application
st.title("PDF Uploader")

# File uploader allows user to add their own PDF
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    # Displaying the file
    st.write("Uploaded PDF file:")

    # Load the PDF file
    pdf = fitz.open("pdf", bytes_data)
    page = pdf.load_page(0)  # 0 is the first page
    pix = page.get_pixmap()
    img_data = pix.tobytes("ppm")
    pdf.close()

    # Convert to a format that streamlit can display
    image = io.BytesIO(img_data)
    st.image(image, caption="First page of the PDF", use_column_width=True)

    # Generate and display test data as a dataframe
    test_data = pd.read_csv("output.csv")
    st.write("Displaying data:")
    st.dataframe(test_data)
else:
    st.write("Please upload a PDF file to display the test data.")
