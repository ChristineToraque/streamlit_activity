import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="Academic Success Visualization", layout="wide")
st.title("🎓 Academic Success Dataset Explorer (Cleaned Data Structure)")

CSV_FILE_PATH = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vStNgdBA_efS0GWpOupXK2q7vsN7nhLuohfZbMqnjRppAKfnBtpjcgUTM1dwJ1nOQ/pub?output=csv'

@st.cache_data(ttl=600)
def load_data(file_path_or_url):
    """Loads data from the given file path or URL."""
    try:
        df = pd.read_csv(file_path_or_url)
        # Handle potential empty first row if CSV was exported from Excel with a title row
        if df.iloc[0].isnull().all():
            df = pd.read_csv(file_path_or_url, skiprows=1)
        if df.columns[0].lower() == 'respondent' and 'respondent' not in df.iloc[0].str.lower().values:
             pass
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df
    except Exception as e:
        st.error(f"Error loading data from {file_path_or_url}: {e}")
        st.error("Please ensure the URL is correct, published to the web as CSV, and accessible, ")
        return pd.DataFrame()

df_original = load_data(CSV_FILE_PATH)

if df_original.empty:
    st.warning("Could not load data. Please check the source path/URL and your internet connection if it's a URL.")
    st.stop()

df = df_original.copy()

st.sidebar.header("⚙️ Display Options")
if st.sidebar.checkbox("Show Raw Data Sample", False):
    st.subheader("📄 Raw Data (First 10 Rows)")
    st.dataframe(df.head(10))

st.sidebar.markdown("---")
st.sidebar.header("📊 Visualization Selection")

new_column_names = [
    'SocioeconomicStatus', 'Attendance', 'ExtracurricularActivities',
    'PsychologicalFactors', 'AcademicPerformanceData', 'StudyHabits', 'Academic Success'
]
cols_to_make_numeric = new_column_names

for col in cols_to_make_numeric:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

graph_options = [
    "1. Histogram: Distribution of Academic Performance",
    "2. Bar Chart: Average Academic Performance by Success Level",
    "3. Scatter Plot: Study Habits vs. Academic Performance",
    "4. Box Plot: Academic Performance by Extracurricular Activities Score",
    "5. Pie Chart: Proportion of Student Academic Success Levels",
    "6. Heatmap: Correlation Between Key Factors"
]
selected_graph = st.sidebar.selectbox("Choose a graph to display:", graph_options)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Graph Specific Options")

st.header("🔍 Exploratory Data Visualizations")
st.markdown(f"#### Displaying: {selected_graph}")

# Define expected column name variables for clarity in plotting functions
col_ses = 'SocioeconomicStatus'
col_attendance = 'Attendance'
col_extracurricular = 'ExtracurricularActivities'
col_psychological = 'PsychologicalFactors'
col_performance = 'AcademicPerformanceData'
col_study_habits = 'StudyHabits'
col_academic_success = 'Academic Success' # Note the space
heatmap_default_cols = new_column_names # All new columns are potential candidates for heatmap

if selected_graph == graph_options[0]:
    # Histogram of AcademicPerformanceData
    target_col = col_performance
    if target_col in df.columns:
        df_cleaned = df.dropna(subset=[target_col])
        if not df_cleaned.empty and pd.api.types.is_numeric_dtype(df_cleaned[target_col]):
            min_bins = 2
            max_bins = max(min_bins, int(df_cleaned[target_col].nunique()))
            default_bins = min(10, max_bins) if max_bins > min_bins else max_bins
            selected_bins = st.sidebar.slider(
                f"Bins for '{target_col}' Histogram:", min_bins, max_bins, default_bins,
                key="hist_bins_perf_selected", step=1 if max_bins > min_bins else 0
            ) if max_bins > min_bins else default_bins
            fig = px.histogram(df_cleaned, x=target_col, nbins=selected_bins, title=f"Distribution of {target_col}")
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Shows the distribution of {target_col.lower()} scores.")
        else: st.warning(f"Column '{target_col}' is not numeric or has no valid data.")
    else: st.warning(f"Column '{target_col}' not found.")

elif selected_graph == graph_options[1]:
    # Bar Chart: Average AcademicPerformanceData by Academic Success level
    cat_col, score_col = col_academic_success, col_performance
    if cat_col in df.columns and score_col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[score_col]):
            st.warning(f"Score column '{score_col}' is not numeric.")
        else:
            df_cleaned = df.dropna(subset=[score_col, cat_col]).copy() # Use .copy() to avoid SettingWithCopyWarning
            df_cleaned.loc[:, cat_col] = df_cleaned[cat_col].astype(str) # Treat success level as category
            if not df_cleaned.empty:
                avg_score_by_cat = df_cleaned.groupby(cat_col)[score_col].mean().reset_index().sort_values(by=score_col, ascending=False)
                fig = px.bar(avg_score_by_cat, x=cat_col, y=score_col, color=cat_col, title=f"Average {score_col} by {cat_col}")
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"Compares average {score_col.lower()} across different '{cat_col.lower()}' levels.")
            else: st.warning(f"No data for bar chart after cleaning for columns '{cat_col}' and '{score_col}'.")
    else: st.warning(f"One or both columns ('{cat_col}', '{score_col}') not found.")

elif selected_graph == graph_options[2]:
    # Scatter Plot: StudyHabits vs. AcademicPerformanceData
    x_col, y_col = col_study_habits, col_performance
    scatter_color_options = [None, col_psychological, col_ses, col_extracurricular, col_attendance, col_academic_success]
    valid_scatter_color_options = [opt for opt in scatter_color_options if opt is None or opt in df.columns]
    default_color_index = valid_scatter_color_options.index(col_psychological) if col_psychological in valid_scatter_color_options else 0

    color_col_selected = st.sidebar.selectbox(
        "Color scatter plot by (optional):",
        options=valid_scatter_color_options,
        index=default_color_index,
        key="scatter_color_new"
    )

    if x_col in df.columns and y_col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
            st.warning(f"Columns for scatter plot ('{x_col}', '{y_col}') must be numeric.")
        else:
            df_cleaned = df.dropna(subset=[x_col, y_col]).copy()
            if color_col_selected and color_col_selected in df.columns:
                df_cleaned = df_cleaned.dropna(subset=[color_col_selected]).copy()
            if not df_cleaned.empty:
                hover_data_cols = [col for col in [col_ses, col_attendance, col_academic_success] if col in df_cleaned.columns]
                fig = px.scatter(df_cleaned, x=x_col, y=y_col, color=color_col_selected,
                                 title=f"{x_col} vs. {y_col}" + (f" (Colored by {color_col_selected})" if color_col_selected else ""),
                                 hover_data=hover_data_cols)
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"Relationship between {x_col.lower()} and {y_col.lower()}.")
            else: st.warning(f"No data for scatter plot after cleaning for columns '{x_col}', '{y_col}'.")
    else: st.warning(f"One or both columns ('{x_col}', '{y_col}') not found.")

elif selected_graph == graph_options[3]:
    # Box Plot: AcademicPerformanceData by ExtracurricularActivities score
    score_col, cat_col = col_performance, col_extracurricular
    if score_col in df.columns and cat_col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[score_col]):
            st.warning(f"Score column '{score_col}' is not numeric.")
        else:
            df_cleaned = df.dropna(subset=[score_col, cat_col]).copy()
            df_cleaned.loc[:, cat_col] = df_cleaned[cat_col].astype(str) # Treat extracurricular score as category
            if not df_cleaned.empty:
                fig = px.box(df_cleaned, x=cat_col, y=score_col, color=cat_col,
                             title=f"{score_col} Distribution by {cat_col} Score")
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"Shows distribution of {score_col.lower()} by {cat_col.lower()} score (treated as categories).")
            else: st.warning(f"No data for box plot after cleaning for columns '{score_col}', '{cat_col}'.")
    else: st.warning(f"One or both columns ('{score_col}', '{cat_col}') not found.")

elif selected_graph == graph_options[4]:
    # Pie Chart: Proportion of Student Academic Success Levels
    target_col = col_academic_success
    if target_col in df.columns:
        df_cleaned = df.dropna(subset=[target_col]).copy()
        df_cleaned.loc[:, target_col] = df_cleaned[target_col].astype(str) # Treat as category
        if not df_cleaned.empty:
            counts = df_cleaned[target_col].value_counts().reset_index()
            counts.columns = [target_col, 'Count']
            fig = px.pie(counts, names=target_col, values='Count', title=f"Proportion of Student {target_col} Levels")
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Visualizes the proportion of students across different '{target_col.lower()}' levels.")
        else: st.warning(f"No data for pie chart after cleaning for column '{target_col}'.")
    else: st.warning(f"Column '{target_col}' not found.")

elif selected_graph == graph_options[5]:
    # Heatmap: Correlation Between Key Factors
    st.sidebar.markdown("**Heatmap Column Selection:**")
    available_numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    actual_default_heatmap_cols = [col for col in heatmap_default_cols if col in available_numeric_cols]

    selected_cols_for_heatmap = st.sidebar.multiselect(
        "Select numerical columns for correlation heatmap:",
        options=available_numeric_cols,
        default=actual_default_heatmap_cols,
        key="heatmap_cols_selected_new"
    )
    if selected_cols_for_heatmap and len(selected_cols_for_heatmap) >=2:
        df_heatmap = df[selected_cols_for_heatmap].copy().dropna()
        if not df_heatmap.empty and df_heatmap.shape[0] > 1:
            correlation_matrix = df_heatmap.corr()
            fig_heatmap, ax_heatmap = plt.subplots(figsize=(max(8, len(selected_cols_for_heatmap)*0.8), max(6, len(selected_cols_for_heatmap)*0.6)))
            sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5, ax=ax_heatmap, annot_kws={"size":8})
            plt.title("Correlation Matrix of Selected Factors", fontsize=14)
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.yticks(rotation=0, fontsize=10)
            plt.tight_layout()
            st.pyplot(fig_heatmap)
            st.caption("Pearson correlation coefficients between selected factors.")
        else: st.warning("Not enough valid data rows for heatmap after cleaning, or too few columns selected.")
    elif selected_cols_for_heatmap and len(selected_cols_for_heatmap) < 2:
        st.info("Select at least two numerical columns for the correlation heatmap.")
    else:
        st.info("Select numerical columns from the sidebar for the heatmap.")

st.markdown("---")
if CSV_FILE_PATH.startswith('http'):
    st.markdown(f"📊 Visualizing data from: [Google Sheet]({CSV_FILE_PATH})")
else:
    st.markdown(f"📊 Visualizing data from: **{os.path.basename(CSV_FILE_PATH)}**")
st.markdown("🛠️ Built with Streamlit")
