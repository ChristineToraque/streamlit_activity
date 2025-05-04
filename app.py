import streamlit as st
import pandas as pd

st.title("Streamlit WorkBook!")
st.header("CSV Uploader and Viewer!")
st.write("Ready to upload CSV!")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if df.shape[1] < 5:
        st.error("File data should contain a minimum of 5 columns")
    else:
        st.header("Explore Data!")

        column_to_explore = st.selectbox("Select a column to explore", df.columns)

        # Display unique values for the selected columns
        st.write(f"Unique values in '{column_to_explore}:")
        st.write(df[column_to_explore].unique())

        st.header("Raw Data Viewer")
        if st.checkbox("show raw data"):
            st.write("Here the data from your uploaded csv file")
            st.dataframe(df)
