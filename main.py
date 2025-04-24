import streamlit as st
import pandas as pd
import chardet
from io import BytesIO

st.set_page_config(page_title="File Converter & Cleaner", layout="wide")

#Css
st.markdown("""
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 600;
            color: white;
            margin-bottom: 0.5rem;
        }
        .section-subtitle {
            font-size: 1.1rem;
            color: #360;
            margin-bottom: 1rem;
        }
        .stButton>button {
            background-color: #0066cc;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
        }
        .stButton>button:hover {
            background-color: #0055aa;
        }
        .stRadio > div {
            gap: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">File Converter & Cleaner</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Upload CSV or Excel files, clean missing values, choose columns, and download the final version.</div>', unsafe_allow_html=True)

# Sidebar Upload
with st.sidebar:
    st.header("Upload Files")
    files = st.file_uploader("Upload one or more CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)

# File Processing
if files:
    for file in files:
        ext = file.name.split(".")[-1]

        # Load 
        if ext == "csv":
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result["encoding"]
            file.seek(0)
            df = pd.read_csv(file, encoding=encoding)
        else:
            df = pd.read_excel(file)

        st.markdown("---")
        st.subheader(f"Preview: {file.name}")
        st.dataframe(df.head(), use_container_width=True)

        # Clean
        with st.expander("Clean & Filter Options"):
            col1, col2 = st.columns(2)

            with col1:
                fill_missing = st.checkbox("Fill missing numeric values with column mean")
            with col2:
                selected_columns = st.multiselect("Select columns to keep", df.columns, default=df.columns)

            df = df[selected_columns]

            if fill_missing:
                df.fillna(df.select_dtypes(include="number").mean(), inplace=True)
                st.success("Missing values filled successfully.")

        # Chart
        if st.checkbox("Show Bar Chart (first 2 numeric columns)"):
            numeric_data = df.select_dtypes(include="number")
            if not numeric_data.empty:
                st.bar_chart(numeric_data.iloc[:, :2])
            else:
                st.warning("No numeric columns to display.")

        # File Export
        format_choice = st.radio("Choose file format", ["Excel", "CSV"], horizontal=True)
        if st.button(f"Download cleaned file ({format_choice})", key=file.name):
            output = BytesIO()
            try:
                if format_choice.lower() == "csv":
                    df.to_csv(output, index=False)
                    mime = "text/csv"
                    new_file_name = file.name.replace(ext, "csv")
                else:
                    df.to_excel(output, index=False, engine="openpyxl")
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    new_file_name = file.name.replace(ext, "xlsx")

                output.seek(0)
                st.download_button("Click to Download", data=output, file_name=new_file_name, mime=mime)
                st.success("File ready for download.")

            except ModuleNotFoundError as e:
                if "openpyxl" in str(e):
                    st.error("'openpyxl' module not found. Please install it using: pip install openpyxl")
                else:
                    st.error(f"Error: {e}")
