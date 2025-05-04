import streamlit as st
import pandas as pd
import re

st.title("Streamlit WorkBook!")
st.sidebar.header("Data Source Loader")

uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
show_data = st.sidebar.checkbox("View Raw Data", value=True)

# Helper function to convert CamelCase to Title Case with spaces
def camel_to_space(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1 \2', name)
    name = name.replace('_', ' ')
    name = name[0].upper() + name[1:]
    return name

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if df.shape[1] < 5:
        st.error("File data should contain a minimum of 5 columns")
    else:
        st.header("Explore Data!")

        # Main area tabs
        if show_data:
            tab1, tab2, tab3 = st.tabs(["Column Profiling", "Dataset Overview", "Raw Data"])
        else:
            tab1, tab2 = st.tabs(["Column Profiling", "Dataset Overview"])

        with tab1:
            # Create pretty column names for display
            pretty_columns = {camel_to_space(col): col for col in df.columns}
            selected_pretty_column = st.selectbox(
                "Select attribute (column) to analyze",
                options=pretty_columns.keys()
            )
            column_to_analyze = pretty_columns[selected_pretty_column]

            st.header(f"Profiling Column: {camel_to_space(column_to_analyze)}")
            selected_column = df[column_to_analyze]

            # Display column metadata
            st.markdown(f"**Data Type:** <span style='color: #1E90FF;'>{selected_column.dtype}</span>", unsafe_allow_html=True)

            missing_count = selected_column.isnull().sum()
            missing_color = "red" if missing_count > 0 else "green"
            st.markdown(f"**Number of Missing Values:** <span style='color: {missing_color};'>{missing_count}</span>", unsafe_allow_html=True)
            st.markdown(f"**Number of Unique Values:** <span style='color: #32CD32;'>{selected_column.nunique()}</span>", unsafe_allow_html=True)

            # Show unique values in an expander, especially useful for categorical data
            with st.expander("See Unique Values"):
                 st.write(selected_column.unique())

        with tab2:
            st.header("Dataset Overview")

            # Expander for overall dataset info
            with st.expander("Dataset Profile (Info & Stats)"):
                st.subheader("Dataset Info (`df.info()`)")
                info_df = pd.DataFrame({
                    "Column": df.columns,
                    "Non-Null Count": df.count().values,
                    "Dtype": df.dtypes.values
                })
                st.dataframe(info_df)
                st.write(f"Total Entries: {len(df)}")
                st.write(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")

                st.subheader("Numeric Columns Summary (`df.describe()`)")
                st.dataframe(df.describe())

        if show_data:
            with tab3:
                st.header("Raw Data Preview")
                st.dataframe(df)
else:
    st.info("Please upload a CSV file using sidebar control")
