import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="Academic Success Visualization", layout="wide")
st.title("🎓 Academic Success Dataset Explorer")

CSV_FILE_PATH = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vT-cB95XqxQD5oxtx6ri-fT2ZFKLFofNyD3slVgjdxXha2qF3pFl0PhS_q-N5hxAK1KZ-u9afBF8l0F/pub?output=csv'

@st.cache_data(ttl=600)
def load_data(file_path_or_url):
    """Loads data from the given file path or URL."""
    try:
        df = pd.read_csv(file_path_or_url)
        if df.columns[-1].startswith('Unnamed:'):
            df = df.iloc[:, :-1]
        return df
    except Exception as e:
        st.error(f"Error loading data from {file_path_or_url}: {e}")
        st.error("Please ensure the URL is correct, published to the web as CSV, and accessible, or the local file path is correct.")
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

cols_to_make_numeric = ['Age', 'Gender', 'Course', 'Ylevel', 'Muni', 'FamOcc', 'FamIn', 'AccER', 'ParEn', 'ExpEA', 'PrivT',
                        'Books', 'ExtAc', 'Techn', 'PLCon', 'FinSt', 'Nabst', 'Ab1wk', 'Ab3wk',
                        'Sport', 'Music', 'Dance', 'Clubs', 'Motiv', 'SelfE', 'EmWlB', 'Stress',
                        'Anxiet', 'Deprsn', 'TestS', 'Actvt', 'Prtcpt', 'OralR', 'Redng', 'TakNo', 'JGrSt', 'Success']

for col in cols_to_make_numeric:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        st.sidebar.warning(f"Column '{col}' intended for numeric conversion was not found in the dataset from the source.")


graph_options = [
    "1. Histogram: Distribution of Motivation Scores",
    "2. Bar Chart: Average Motivation Score by Gender",
    "3. Scatter Plot: Technology Access vs. Motivation Score",
    "4. Box Plot: Motivation Score Distribution by Extracurricular Activities",
    "5. Pie Chart: Proportion of Student Success",
    "6. Heatmap: Correlation Between Numerical Features"
]
selected_graph = st.sidebar.selectbox("Choose a graph to display:", graph_options)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Graph Specific Options")


st.header("🔍 Exploratory Data Visualizations")
st.markdown(f"#### Displaying: {selected_graph}")

if selected_graph == graph_options[0]:
    score_col_hist = 'Motiv'
    if score_col_hist in df.columns:
        df_cleaned_hist = df.dropna(subset=[score_col_hist])
        if not df_cleaned_hist.empty and pd.api.types.is_numeric_dtype(df_cleaned_hist[score_col_hist]):
            min_bins = 2
            max_bins = max(min_bins, int(df_cleaned_hist[score_col_hist].nunique()))
            default_bins = min(10, max_bins) if max_bins > min_bins else max_bins

            selected_bins_score = st.sidebar.slider(
                f"Select number of bins for '{score_col_hist}' Histogram:",
                min_value=min_bins,
                max_value=max_bins,
                value=default_bins,
                key="hist_bins_motiv_selected",
                step=1 if max_bins > min_bins else 0
            ) if max_bins > min_bins else default_bins

            fig_score_hist = px.histogram(df_cleaned_hist, x=score_col_hist, nbins=selected_bins_score,
                                          title=f"Distribution of {score_col_hist}",
                                          labels={score_col_hist: "Motivation Score"})
            fig_score_hist.update_layout(bargap=0.1)
            st.plotly_chart(fig_score_hist, use_container_width=True)
            st.caption("Shows the distribution of student motivation scores.")
        elif not df_cleaned_hist.empty:
            st.warning(f"Column '{score_col_hist}' is not numeric and cannot be used for a histogram.")
        else:
            st.warning(f"No valid data found in column '{score_col_hist}' for histogram after dropping NaNs.")
    else:
        st.warning(f"Column '{score_col_hist}' not found in the dataset for 'Motivation Scores' histogram.")

elif selected_graph == graph_options[1]:
    cat_col_bar = 'Gender'
    score_col_bar_avg = 'Motiv'

    if cat_col_bar in df.columns and score_col_bar_avg in df.columns:
        if not pd.api.types.is_numeric_dtype(df[score_col_bar_avg]):
            st.warning(f"Score column '{score_col_bar_avg}' for bar chart is not numeric. Cannot calculate average.")
        else:
            df_cleaned_bar = df.dropna(subset=[score_col_bar_avg, cat_col_bar])
            df_cleaned_bar[cat_col_bar] = df_cleaned_bar[cat_col_bar].astype(str)

            if not df_cleaned_bar.empty:
                avg_score_by_cat = df_cleaned_bar.groupby(cat_col_bar)[score_col_bar_avg].mean().reset_index()
                avg_score_by_cat = avg_score_by_cat.sort_values(by=score_col_bar_avg, ascending=False)

                fig_avg_score_bar = px.bar(avg_score_by_cat, x=cat_col_bar, y=score_col_bar_avg,
                                           title=f"Average {score_col_bar_avg} by {cat_col_bar}",
                                           labels={cat_col_bar: "Gender (Encoded)", score_col_bar_avg: f"Average {score_col_bar_avg}"},
                                           color=cat_col_bar)
                st.plotly_chart(fig_avg_score_bar, use_container_width=True)
                st.caption(f"Compares the average motivation score across different genders (numeric codes shown).")
            else:
                st.warning(f"Not enough valid data in '{cat_col_bar}' or '{score_col_bar_avg}' for the bar chart after cleaning.")
    else:
        st.warning(f"One or both columns ('{cat_col_bar}', '{score_col_bar_avg}') not found for the bar chart.")

elif selected_graph == graph_options[2]:
    x_col_scatter = 'Techn'
    y_col_scatter = 'Motiv'

    scatter_color_options = [None] + [col for col in df.columns if df[col].nunique() < 15 and col not in [x_col_scatter, y_col_scatter]]
    color_col_scatter = st.sidebar.selectbox("Color scatter plot by (optional):", options=scatter_color_options, index=scatter_color_options.index('Gender') if 'Gender' in scatter_color_options else 0, key="scatter_color")


    if x_col_scatter in df.columns and y_col_scatter in df.columns:
        if not pd.api.types.is_numeric_dtype(df[x_col_scatter]) or not pd.api.types.is_numeric_dtype(df[y_col_scatter]):
            st.warning(f"One or both columns for scatter plot ('{x_col_scatter}', '{y_col_scatter}') are not numeric.")
        else:
            df_cleaned_scatter = df.dropna(subset=[x_col_scatter, y_col_scatter])
            if color_col_scatter and color_col_scatter in df.columns:
                df_cleaned_scatter = df_cleaned_scatter.dropna(subset=[color_col_scatter])
                df_cleaned_scatter[color_col_scatter] = df_cleaned_scatter[color_col_scatter].astype(str)

            if not df_cleaned_scatter.empty:
                hover_cols = ['Course', 'Ylevel']
                if 'Success' in df_cleaned_scatter.columns:
                    hover_cols.append('Success')

                fig_study_score_scatter = px.scatter(df_cleaned_scatter, x=x_col_scatter, y=y_col_scatter,
                                                     color=color_col_scatter if color_col_scatter in df_cleaned_scatter.columns else None,
                                                     title=f"{x_col_scatter} vs. {y_col_scatter}",
                                                     labels={x_col_scatter: "Technology Access Score", y_col_scatter: "Motivation Score", color_col_scatter: f"{color_col_scatter} (Encoded)" if color_col_scatter else "Color"},
                                                     hover_data=hover_cols)
                fig_study_score_scatter.update_traces(marker=dict(size=8, opacity=0.7))
                st.plotly_chart(fig_study_score_scatter, use_container_width=True)
                st.caption(f"Shows the relationship between technology access score and motivation score. Each point is a student.")
            else:
                st.warning(f"Not enough valid data in '{x_col_scatter}' or '{y_col_scatter}' for the scatter plot after cleaning.")
    else:
        st.warning(f"One or both columns ('{x_col_scatter}', '{y_col_scatter}') not found for the scatter plot.")

elif selected_graph == graph_options[3]:
    score_col_box = 'Motiv'
    cat_col_box = 'ExtAc'

    if score_col_box in df.columns and cat_col_box in df.columns:
        if not pd.api.types.is_numeric_dtype(df[score_col_box]):
             st.warning(f"Score column '{score_col_box}' for box plot is not numeric.")
        else:
            df_cleaned_box = df.dropna(subset=[score_col_box, cat_col_box])
            df_cleaned_box[cat_col_box] = df_cleaned_box[cat_col_box].astype(str)

            if not df_cleaned_box.empty:
                fig_score_cat_box = px.box(df_cleaned_box, x=cat_col_box, y=score_col_box,
                                           color=cat_col_box,
                                           title=f"{score_col_box} Distribution by {cat_col_box}",
                                           labels={cat_col_box: "Extracurricular Activities (Encoded)", score_col_box: "Motivation Score"})
                st.plotly_chart(fig_score_cat_box, use_container_width=True)
                st.caption(f"Displays the distribution of motivation scores for different levels/types of extracurricular activity participation (numeric codes shown).")
            else:
                st.warning(f"Not enough valid data in '{score_col_box}' or '{cat_col_box}' for the box plot after cleaning.")
    else:
        st.warning(f"One or both columns ('{score_col_box}', '{cat_col_box}') not found for the box plot.")

elif selected_graph == graph_options[4]:
    outcome_col_pie = 'Success'

    if outcome_col_pie in df.columns:
        df_cleaned_pie = df.dropna(subset=[outcome_col_pie])
        df_cleaned_pie[outcome_col_pie] = df_cleaned_pie[outcome_col_pie].astype(str)

        if not df_cleaned_pie.empty:
            outcome_counts = df_cleaned_pie[outcome_col_pie].value_counts().reset_index()
            outcome_counts.columns = [outcome_col_pie, 'Count']

            fig_pie_outcome = px.pie(outcome_counts, names=outcome_col_pie, values='Count',
                                     title=f"Proportion of Student {outcome_col_pie}",
                                     color=outcome_col_pie)
            fig_pie_outcome.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie_outcome, use_container_width=True)
            st.caption(f"Visualizes the proportion of students based on the '{outcome_col_pie}' column (numeric codes shown as categories).")
        else:
            st.warning(f"Not enough valid data in '{outcome_col_pie}' for the pie chart after cleaning.")
    else:
        st.warning(f"Column '{outcome_col_pie}' not found for the pie chart. Ensure your data source has a 'Success' column.")

elif selected_graph == graph_options[5]:
    default_heatmap_cols = ['Motiv', 'SelfE', 'Stress', 'Anxiet', 'Deprsn', 'TestS', 'PLCon', 'FinSt', 'Techn', 'Books']
    if 'Success' in df.columns and pd.api.types.is_numeric_dtype(df['Success']):
        default_heatmap_cols.append('Success')

    initial_heatmap_cols = [col for col in default_heatmap_cols if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

    st.sidebar.markdown("**Heatmap Column Selection:**")
    available_numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    numerical_cols_for_heatmap = st.sidebar.multiselect(
        "Select numerical columns for correlation heatmap:",
        options=available_numeric_cols,
        default=[col for col in initial_heatmap_cols if col in available_numeric_cols],
        key="heatmap_cols_selected"
    )

    if numerical_cols_for_heatmap and all(col in df.columns for col in numerical_cols_for_heatmap):
        df_heatmap_data = df[numerical_cols_for_heatmap].copy()
        df_heatmap_data.dropna(inplace=True)

        if not df_heatmap_data.empty and df_heatmap_data.shape[1] >= 2:
            correlation_matrix = df_heatmap_data.corr()
            fig_heatmap, ax_heatmap = plt.subplots(figsize=(max(10, len(numerical_cols_for_heatmap)), max(8, len(numerical_cols_for_heatmap) * 0.8)))
            sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5, ax=ax_heatmap, annot_kws={"size":8})
            ax_heatmap.set_title("Correlation Matrix of Selected Numerical Features", fontsize=16)
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            plt.tight_layout()
            st.pyplot(fig_heatmap)
            st.caption("Shows Pearson correlation coefficients. Values close to 1 or -1 indicate a strong positive or negative linear relationship, respectively.")
        elif df_heatmap_data.shape[1] < 2:
            st.warning("Please select at least two valid numerical columns for the correlation heatmap.")
        else:
            st.warning("Not enough valid numerical data in the selected columns for the heatmap after cleaning and dropping NaNs.")
    elif not numerical_cols_for_heatmap:
        st.info("Select at least two numerical columns from the sidebar to generate a correlation heatmap.")
    else:
        st.warning("One or more selected columns for the heatmap are not found or are not suitable. Please check your selection.")

st.markdown("---")
if CSV_FILE_PATH.startswith('http'):
    st.markdown(f"📊 Visualizing data from: [Google Sheet]({CSV_FILE_PATH})")
else:
    st.markdown(f"📊 Visualizing data from: **{os.path.basename(CSV_FILE_PATH)}**")
st.markdown("🛠️ Built with Streamlit")
