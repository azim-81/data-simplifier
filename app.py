import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import re

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Data Simplifier",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("📊 Data Simplifier")
st.write(
    "Clean, understand and explore your spreadsheet with a few simple steps."
)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:
    st.header("📂 Upload Dataset")

    uploaded = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx"]
    )

    st.caption("Personal learning project • Mohd Azeem")

# ---------------------------------------------------------
# NO FILE
# ---------------------------------------------------------

if uploaded is None:

    st.info("Upload a CSV or Excel file to begin.")

    st.subheader("What can Data Simplifier do?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🧹 Clean")
        st.write(
            "Find and remove duplicates, handle missing values "
            "and tidy column names."
        )

    with col2:
        st.markdown("### 🔍 Understand")
        st.write(
            "View data types, statistics, missing values, "
            "unique values and data quality."
        )

    with col3:
        st.markdown("### 📊 Explore")
        st.write(
            "Create histograms, bar charts, scatter plots, "
            "box plots and correlation analysis."
        )

    st.divider()

    st.subheader("Built with")
    st.write("Python · Pandas · NumPy · Streamlit · Plotly")

    st.stop()


# ---------------------------------------------------------
# READ FILE
# ---------------------------------------------------------

try:

    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)

    else:
        df = pd.read_excel(uploaded)

except Exception as e:

    st.error(f"❌ I couldn't read this file: {e}")
    st.stop()


# ---------------------------------------------------------
# BASIC VALIDATION
# ---------------------------------------------------------

if df.empty:

    st.warning("The file was read, but it does not contain any rows.")
    st.stop()


# Original dataset
original = df.copy()

# Store cleaned data
if "cleaned" not in st.session_state:
    st.session_state.cleaned = df.copy()

if "changes" not in st.session_state:
    st.session_state.changes = []


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def calculate_quality_score(data):

    if data.empty:
        return 0

    total_cells = data.shape[0] * data.shape[1]

    if total_cells == 0:
        return 0

    missing = data.isna().sum().sum()

    duplicates = data.duplicated().sum()

    missing_ratio = missing / total_cells
    duplicate_ratio = duplicates / len(data)

    score = 100 - ((missing_ratio * 70) + (duplicate_ratio * 30) * 100)

    return max(0, min(100, score))


def clean_column_names(columns):

    new_columns = []

    for column in columns:

        name = str(column).strip().lower()

        name = re.sub(r"\s+", "_", name)

        name = re.sub(r"[^a-zA-Z0-9_]", "", name)

        name = re.sub(r"_+", "_", name)

        name = name.strip("_")

        if not name:
            name = "column"

        new_columns.append(name)

    # Make duplicate column names unique
    final_columns = []
    counter = {}

    for name in new_columns:

        if name not in counter:
            counter[name] = 0
            final_columns.append(name)

        else:
            counter[name] += 1
            final_columns.append(f"{name}_{counter[name]}")

    return final_columns


def detect_outliers(data, column):

    if column not in data.columns:
        return pd.Series(False, index=data.index)

    series = pd.to_numeric(data[column], errors="coerce")

    if series.dropna().empty:
        return pd.Series(False, index=data.index)

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    iqr = q3 - q1

    if iqr == 0:
        return pd.Series(False, index=data.index)

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return (series < lower) | (series > upper)


def dataframe_to_excel(data):

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data.to_excel(
            writer,
            index=False,
            sheet_name="Cleaned Data"
        )

    return output.getvalue()


# ---------------------------------------------------------
# DATA QUALITY
# ---------------------------------------------------------

missing_cells = int(df.isna().sum().sum())
duplicate_rows = int(df.duplicated().sum())
quality_score = calculate_quality_score(df)


# ---------------------------------------------------------
# MAIN TABS
# ---------------------------------------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Overview",
        "🧠 Smart Clean",
        "🧹 Clean Data",
        "🔎 Analyze",
        "📈 Visualize",
        "💾 Export"
    ]
)


# =========================================================
# TAB 1 — OVERVIEW
# =========================================================

with tab1:

    st.subheader("Dataset Overview")

    # Metrics
    a, b, c, d, e = st.columns(5)

    a.metric(
        "Rows",
        f"{len(df):,}"
    )

    b.metric(
        "Columns",
        f"{len(df.columns):,}"
    )

    c.metric(
        "Missing Cells",
        f"{missing_cells:,}"
    )

    d.metric(
        "Duplicate Rows",
        f"{duplicate_rows:,}"
    )

    e.metric(
        "Quality Score",
        f"{quality_score:.0f}%"
    )

    st.divider()

    # Quality message

    if quality_score >= 90:
        st.success("🟢 Your dataset looks relatively clean.")

    elif quality_score >= 70:
        st.warning("🟡 Your dataset has some quality issues.")

    else:
        st.error("🔴 Your dataset needs significant cleaning.")

    # -----------------------------------------------------
    # COLUMN PROFILE
    # -----------------------------------------------------

    st.subheader("📋 Column Profile")

    profile = pd.DataFrame({
        "Column": df.columns,
        "Data Type": [str(x) for x in df.dtypes],
        "Missing": df.isna().sum().values,
        "Missing %": [
            round(df[x].isna().mean() * 100, 2)
            for x in df.columns
        ],
        "Unique": [
            df[x].nunique(dropna=True)
            for x in df.columns
        ]
    })

    st.dataframe(
        profile,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # FIRST ROWS
    # -----------------------------------------------------

    st.subheader("👀 Preview")

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # DATA TYPES
    # -----------------------------------------------------

    st.subheader("🔢 Data Types")

    type_counts = df.dtypes.astype(str).value_counts()

    fig = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title="Data Type Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# TAB 2 — CLEAN DATA
# =========================================================

with tab2:

    st.subheader("🧹 Clean Your Dataset")

    st.write(
        "Choose the cleaning operations you want to perform."
    )

 

 # -----------------------------------------------------
# MISSING VALUE HANDLING
# -----------------------------------------------------

st.markdown("### 1. 🧹 Missing Values")

missing_summary = pd.DataFrame({
    "Column": df.columns,
    "Missing": df.isna().sum().values,
    "Missing %": [
        round(df[column].isna().mean() * 100, 2)
        for column in df.columns
    ]
})

missing_summary = missing_summary[
    missing_summary["Missing"] > 0
].copy()

if missing_summary.empty:

    st.success("✅ No missing values were found in your dataset.")

else:

    st.write(
        f"Found **{missing_summary['Missing'].sum():,} missing cells** "
        f"across **{len(missing_summary)} column(s)**."
    )

    st.dataframe(
        missing_summary,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Choose how to handle each column")

    missing_actions = {}

    for column in missing_summary["Column"]:

        missing_count = int(
            df[column].isna().sum()
        )

        dtype = df[column].dtype

        # Automatic suggestion
        if pd.api.types.is_numeric_dtype(dtype):
            default_action = "Fill with median"

        else:
            default_action = "Fill with mode"

        options = [
            "Keep missing values",
            "Remove rows",
            "Fill with mean",
            "Fill with median",
            "Fill with mode",
            "Fill with 0",
            "Fill with custom value"
        ]

        default_index = options.index(
            default_action
        )

        action = st.selectbox(
            f"**{column}** — {missing_count:,} missing value(s)",
            options,
            index=default_index,
            key=f"missing_action_{column}"
        )

        missing_actions[column] = action

        # Custom value
        if action == "Fill with custom value":

            custom_value = st.text_input(
                f"Value for '{column}'",
                key=f"custom_value_{column}"
            )

            missing_actions[column] = (
                action,
                custom_value
            )

    st.divider()

# -----------------------------------------------------
# DUPLICATE ROW HANDLING
# -----------------------------------------------------

st.markdown("### 2. 🔁 Duplicate Rows")

duplicate_count = int(df.duplicated().sum())

if duplicate_count == 0:

    st.success("✅ No duplicate rows were found.")

    remove_duplicates = False

else:

    st.warning(
        f"⚠️ Found **{duplicate_count:,} duplicate row(s)**."
    )

    # Show duplicates
    show_duplicates = st.checkbox(
        "Show duplicate rows",
        value=False
    )

    if show_duplicates:

        duplicate_rows = df[
            df.duplicated(keep=False)
        ]

        st.dataframe(
            duplicate_rows,
            use_container_width=True,
            hide_index=True
        )

    remove_duplicates = st.checkbox(
        "Remove duplicate rows",
        value=True
    )

    if remove_duplicates:

        duplicate_method = st.radio(
            "How should duplicates be handled?",
            [
                "Keep the first occurrence",
                "Remove every occurrence of duplicated rows"
            ]
        )

        if duplicate_method == "Keep the first occurrence":

            rows_after = len(df.drop_duplicates())

        else:

            duplicated_mask = df.duplicated(
                keep=False
            )

            rows_after = len(
                df[~duplicated_mask]
            )

        rows_to_remove = len(df) - rows_after

        st.info(
            f"📉 This will remove approximately "
            f"**{rows_to_remove:,} row(s)**."
        )

    # -----------------------------------------------------
    # COLUMN NAMES
    # -----------------------------------------------------

    st.markdown("### 3. Column Names")

    tidy_names = st.checkbox(
        "Clean and standardize column names",
        value=True
    )

    # -----------------------------------------------------
    # EMPTY ROWS / COLUMNS
    # -----------------------------------------------------

    remove_empty = st.checkbox(
        "Remove completely empty rows and columns",
        value=True
    )

    # -----------------------------------------------------
    # DATA TYPE CONVERSION
    # -----------------------------------------------------

    st.markdown("### 4. Data Types")

    convert_numbers = st.checkbox(
        "Automatically convert numeric-looking columns",
        value=False
    )

    # -----------------------------------------------------
    # OUTLIERS
    # -----------------------------------------------------

    st.markdown("### 5. Outliers")

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    remove_outliers = st.checkbox(
        "Remove outliers using the IQR method",
        value=False
    )

    outlier_column = None

    if numeric_columns and remove_outliers:

        outlier_column = st.selectbox(
            "Choose column for outlier detection",
            numeric_columns
        )

    # -----------------------------------------------------
    # CLEAN BUTTON
    # -----------------------------------------------------

    st.divider()

    if st.button(
        "✨ Clean My Data",
        type="primary",
        use_container_width=True
    ):

        cleaned = original.copy()

        changes = []

        # Remove empty rows/columns
        if remove_empty:

            before_rows, before_cols = cleaned.shape

            cleaned = cleaned.dropna(
                axis=0,
                how="all"
            )

            cleaned = cleaned.dropna(
                axis=1,
                how="all"
            )

            removed_rows = before_rows - cleaned.shape[0]
            removed_cols = before_cols - cleaned.shape[1]

            if removed_rows or removed_cols:

                changes.append(
                    f"Removed {removed_rows} empty row(s) "
                    f"and {removed_cols} empty column(s)."
                )

        # Clean names
        if tidy_names:

            old_names = list(cleaned.columns)

            cleaned.columns = clean_column_names(
                cleaned.columns
            )

            changed = sum(
                a != b
                for a, b in zip(
                    old_names,
                    cleaned.columns
                )
            )

            if changed:

                changes.append(
                    f"Standardized {changed} column name(s)."
                )

        # Convert numbers
        if convert_numbers:

            converted = 0

            for column in cleaned.columns:

                if cleaned[column].dtype == "object":

                    converted_column = pd.to_numeric(
                        cleaned[column],
                        errors="coerce"
                    )

                    original_non_null = (
                        cleaned[column].notna().sum()
                    )

                    converted_non_null = (
                        converted_column.notna().sum()
                    )

                    if (
                        converted_non_null > 0
                        and converted_non_null >= original_non_null * 0.8
                    ):

                        cleaned[column] = converted_column

                        converted += 1

            if converted:

                changes.append(
                    f"Converted {converted} column(s) to numeric data types."
                )

        # Missing values
        if missing_method != "Do nothing":

            before_missing = int(
                cleaned.isna().sum().sum()
            )

            if missing_method == "Remove rows containing missing values":

                cleaned = cleaned.dropna()

            elif missing_method == "Fill numeric values with mean":

                for column in cleaned.select_dtypes(
                    include=np.number
                ).columns:

                    cleaned[column] = cleaned[column].fillna(
                        cleaned[column].mean()
                    )

            elif missing_method == "Fill numeric values with median":

                for column in cleaned.select_dtypes(
                    include=np.number
                ).columns:

                    cleaned[column] = cleaned[column].fillna(
                        cleaned[column].median()
                    )

            elif missing_method == "Fill numeric values with 0":

                for column in cleaned.select_dtypes(
                    include=np.number
                ).columns:

                    cleaned[column] = cleaned[column].fillna(0)

            elif missing_method == "Fill text values with mode":

                for column in cleaned.columns:

                    if cleaned[column].isna().any():

                        mode = cleaned[column].mode()

                        if not mode.empty:

                            cleaned[column] = cleaned[column].fillna(
                                mode.iloc[0]
                            )

            after_missing = int(
                cleaned.isna().sum().sum()
            )

            handled = before_missing - after_missing

            if handled:

                changes.append(
                    f"Handled {handled:,} missing value(s)."
                )

        # Remove duplicates
        if remove_duplicates:

            before = len(cleaned)

            cleaned = cleaned.drop_duplicates()

            removed = before - len(cleaned)

            if removed:

                changes.append(
                    f"Removed {removed:,} duplicate row(s)."
                )

        # Remove outliers
        if remove_outliers and outlier_column:

            mask = detect_outliers(
                cleaned,
                outlier_column
            )

            removed = int(mask.sum())

            cleaned = cleaned.loc[~mask].copy()

            if removed:

                changes.append(
                    f"Removed {removed:,} outlier row(s) "
                    f"from '{outlier_column}'."
                )

        # Save
        st.session_state.cleaned = cleaned
        st.session_state.changes = changes

        st.success("✅ Cleaning completed successfully!")


    # -----------------------------------------------------
    # CLEANING RESULTS
    # -----------------------------------------------------

    if "cleaned" in st.session_state:

        cleaned = st.session_state.cleaned
        changes = st.session_state.changes

        st.divider()

        st.subheader("📋 Cleaning Summary")

        if changes:

            for change in changes:

                st.write("• " + change)

        else:

            st.info(
                "No changes were necessary with the selected options."
            )

        # Before / After

        left, right = st.columns(2)

        with left:

            st.markdown("### Before")

            st.metric(
                "Rows",
                f"{len(original):,}"
            )

            st.metric(
                "Columns",
                f"{len(original.columns):,}"
            )

        with right:

            st.markdown("### After")

            st.metric(
                "Rows",
                f"{len(cleaned):,}"
            )

            st.metric(
                "Columns",
                f"{len(cleaned.columns):,}"
            )

        st.subheader("Cleaned Data")

        st.dataframe(
            cleaned.head(100),
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# TAB 3 — ANALYZE
# =========================================================

with tab3:

    st.subheader("🔎 Analyze Your Dataset")

    cleaned = st.session_state.cleaned

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    st.markdown("### 🔍 Search Dataset")

    search = st.text_input(
        "Search for a value across the dataset",
        placeholder="Example: John, Delhi, Product A..."
    )

    if search:

        mask = cleaned.astype(str).apply(
            lambda row: row.str.contains(
                search,
                case=False,
                na=False
            ).any(),
            axis=1
        )

        filtered = cleaned[mask]

        st.write(
            f"Found **{len(filtered):,}** matching row(s)."
        )

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    st.divider()

    st.markdown("### 📈 Descriptive Statistics")

    numeric = cleaned.select_dtypes(
        include=np.number
    )

    if not numeric.empty:

        st.dataframe(
            numeric.describe().T,
            use_container_width=True
        )

    else:

        st.info(
            "No numeric columns are available for statistical analysis."
        )

    # -----------------------------------------------------
    # OUTLIER REPORT
    # -----------------------------------------------------

    st.markdown("### 🚨 Outlier Report")

    if not numeric.empty:

        outlier_data = []

        for column in numeric.columns:

            mask = detect_outliers(
                cleaned,
                column
            )

            outlier_data.append({
                "Column": column,
                "Outliers": int(mask.sum()),
                "Percentage": round(
                    mask.mean() * 100,
                    2
                )
            })

        outlier_df = pd.DataFrame(
            outlier_data
        )

        st.dataframe(
            outlier_df,
            use_container_width=True,
            hide_index=True
        )

    # -----------------------------------------------------
    # CORRELATION
    # -----------------------------------------------------

    st.markdown("### 🔗 Correlation")

    if len(numeric.columns) >= 2:

        correlation = numeric.corr()

        fig = px.imshow(
            correlation,
            text_auto=True,
            title="Correlation Matrix"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "At least two numeric columns are needed for correlation analysis."
        )


# =========================================================
# TAB 4 — VISUALIZE / CHART BUILDER
# =========================================================

with tab4:

    st.subheader("📈 Chart Builder")

    cleaned = st.session_state.cleaned.copy()

    numeric = cleaned.select_dtypes(
        include=np.number
    ).columns.tolist()

    categorical = cleaned.select_dtypes(
        exclude=np.number
    ).columns.tolist()

    all_columns = cleaned.columns.tolist()

    if not all_columns:

        st.warning("No columns are available for visualization.")

    else:

        # -------------------------------------------------
        # CHART TYPE
        # -------------------------------------------------

        st.markdown("### 1. Choose a chart")

        chart_type = st.selectbox(
            "Chart type",
            [
                "Bar Chart",
                "Line Chart",
                "Pie Chart",
                "Histogram",
                "Scatter Plot",
                "Box Plot"
            ]
        )

        st.divider()

        # -------------------------------------------------
        # BAR CHART
        # -------------------------------------------------

        if chart_type == "Bar Chart":

            st.markdown("### 📊 Bar Chart")

            if not categorical:

                st.info(
                    "A bar chart works best with categorical columns."
                )

            else:

                col1, col2 = st.columns(2)

                with col1:

                    x_column = st.selectbox(
                        "Category",
                        categorical,
                        key="bar_x"
                    )

                with col2:

                    value_options = [
                        "Count"
                    ] + numeric

                    value_column = st.selectbox(
                        "Value",
                        value_options,
                        key="bar_value"
                    )

                if value_column == "Count":

                    chart_data = (
                        cleaned[x_column]
                        .astype(str)
                        .value_counts()
                        .reset_index()
                    )

                    chart_data.columns = [
                        x_column,
                        "Count"
                    ]

                    y_column = "Count"

                else:

                    chart_data = (
                        cleaned
                        .groupby(x_column)[value_column]
                        .sum()
                        .reset_index()
                    )

                    y_column = value_column

                # Top N
                top_n = st.slider(
                    "Number of categories to show",
                    min_value=3,
                    max_value=min(30, len(chart_data)),
                    value=min(10, len(chart_data)),
                    key="bar_top_n"
                )

                sort_order = st.radio(
                    "Sort",
                    ["Highest first", "Lowest first"],
                    horizontal=True,
                    key="bar_sort"
                )

                chart_data = chart_data.sort_values(
                    y_column,
                    ascending=(sort_order == "Lowest first")
                ).head(top_n)

                title = st.text_input(
                    "Chart title",
                    f"{y_column} by {x_column}",
                    key="bar_title"
                )

                fig = px.bar(
                    chart_data,
                    x=x_column,
                    y=y_column,
                    title=title,
                    text_auto=True
                )

                fig.update_layout(
                    xaxis_title=x_column,
                    yaxis_title=y_column
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # -------------------------------------------------
        # LINE CHART
        # -------------------------------------------------

        elif chart_type == "Line Chart":

            st.markdown("### 📈 Line Chart")

            if not numeric:

                st.info(
                    "A line chart requires at least one numeric column."
                )

            else:

                col1, col2 = st.columns(2)

                with col1:

                    x_column = st.selectbox(
                        "X-axis",
                        all_columns,
                        key="line_x"
                    )

                with col2:

                    y_column = st.selectbox(
                        "Y-axis",
                        numeric,
                        key="line_y"
                    )

                # Try to interpret dates
                line_data = cleaned.copy()

                if line_data[x_column].dtype == "object":

                    try:

                        converted_dates = pd.to_datetime(
                            line_data[x_column],
                            errors="coerce"
                        )

                        if converted_dates.notna().mean() >= 0.7:

                            line_data[x_column] = converted_dates
                            line_data = line_data.sort_values(
                                x_column
                            )

                    except Exception:
                        pass

                title = st.text_input(
                    "Chart title",
                    f"{y_column} over {x_column}",
                    key="line_title"
                )

                fig = px.line(
                    line_data,
                    x=x_column,
                    y=y_column,
                    title=title,
                    markers=True
                )

                fig.update_layout(
                    xaxis_title=x_column,
                    yaxis_title=y_column
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # -------------------------------------------------
        # PIE CHART
        # -------------------------------------------------

        elif chart_type == "Pie Chart":

            st.markdown("### 🥧 Pie Chart")

            if not categorical:

                st.info(
                    "A pie chart requires a categorical column."
                )

            else:

                category_column = st.selectbox(
                    "Category",
                    categorical,
                    key="pie_category"
                )

                pie_data = (
                    cleaned[category_column]
                    .astype(str)
                    .value_counts()
                    .head(10)
                    .reset_index()
                )

                pie_data.columns = [
                    category_column,
                    "Count"
                ]

                title = st.text_input(
                    "Chart title",
                    f"Distribution of {category_column}",
                    key="pie_title"
                )

                fig = px.pie(
                    pie_data,
                    names=category_column,
                    values="Count",
                    title=title,
                    hole=0.35
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # -------------------------------------------------
        # HISTOGRAM
        # -------------------------------------------------

        elif chart_type == "Histogram":

            st.markdown("### 📊 Histogram")

            if not numeric:

                st.info(
                    "No numeric columns were found."
                )

            else:

                column = st.selectbox(
                    "Numeric column",
                    numeric,
                    key="hist_column"
                )

                bins = st.slider(
                    "Number of bins",
                    min_value=5,
                    max_value=100,
                    value=30,
                    key="hist_bins"
                )

                title = st.text_input(
                    "Chart title",
                    f"Distribution of {column}",
                    key="hist_title"
                )

                fig = px.histogram(
                    cleaned,
                    x=column,
                    nbins=bins,
                    title=title
                )

                fig.update_layout(
                    xaxis_title=column,
                    yaxis_title="Count"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # -------------------------------------------------
        # SCATTER PLOT
        # -------------------------------------------------

        elif chart_type == "Scatter Plot":

            st.markdown("### 🔵 Scatter Plot")

            if len(numeric) < 2:

                st.info(
                    "At least two numeric columns are required."
                )

            else:

                col1, col2 = st.columns(2)

                with col1:

                    x_column = st.selectbox(
                        "X-axis",
                        numeric,
                        key="scatter_x_new"
                    )

                with col2:

                    y_options = [
                        column
                        for column in numeric
                        if column != x_column
                    ]

                    y_column = st.selectbox(
                        "Y-axis",
                        y_options,
                        key="scatter_y_new"
                    )

                color_column = None

                if categorical:

                    use_color = st.checkbox(
                        "Color points by category",
                        key="scatter_color"
                    )

                    if use_color:

                        color_column = st.selectbox(
                            "Color column",
                            categorical,
                            key="scatter_category"
                        )

                title = st.text_input(
                    "Chart title",
                    f"{y_column} vs {x_column}",
                    key="scatter_title"
                )

                fig = px.scatter(
                    cleaned,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    title=title,
                    hover_data=all_columns
                )

                fig.update_layout(
                    xaxis_title=x_column,
                    yaxis_title=y_column
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # -------------------------------------------------
        # BOX PLOT
        # -------------------------------------------------

        elif chart_type == "Box Plot":

            st.markdown("### 📦 Box Plot")

            if not numeric:

                st.info(
                    "No numeric columns were found."
                )

            else:

                column = st.selectbox(
                    "Numeric column",
                    numeric,
                    key="box_column_new"
                )

                category = None

                if categorical:

                    add_category = st.checkbox(
                        "Group by category",
                        key="box_category_enable"
                    )

                    if add_category:

                        category = st.selectbox(
                            "Category",
                            categorical,
                            key="box_category"
                        )

                title = st.text_input(
                    "Chart title",
                    f"Distribution of {column}",
                    key="box_title"
                )

                fig = px.box(
                    cleaned,
                    x=category,
                    y=column,
                    title=title,
                    points="outliers"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # -------------------------------------------------
        # DOWNLOAD CHART
        # -------------------------------------------------

        st.divider()

        st.markdown("### 💡 Chart Tips")

        st.info(
            "Use Bar Charts for category comparisons, "
            "Line Charts for trends, Pie Charts for proportions, "
            "Histograms for distributions, Scatter Plots for relationships, "
            "and Box Plots for distributions and outliers."
        )
# =========================================================
# TAB 5 — EXPORT
# =========================================================

with tab5:

    st.subheader("💾 Export Your Data")

    cleaned = st.session_state.cleaned

    st.write(
        f"Your cleaned dataset contains "
        f"**{len(cleaned):,} rows** and "
        f"**{len(cleaned.columns):,} columns**."
    )

    st.divider()

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # CSV
    # -----------------------------------------------------

    with col1:

        st.markdown("### 📄 CSV")

        csv_data = cleaned.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download CSV",
            csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv",
            use_container_width=True
        )

    # -----------------------------------------------------
    # EXCEL
    # -----------------------------------------------------

    with col2:

        st.markdown("### 📊 Excel")

        excel_data = dataframe_to_excel(
            cleaned
        )

        st.download_button(
            "⬇️ Download Excel",
            excel_data,
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# -----------------------------------------------------
# AUTOMATIC DATA QUALITY REPORT
# -----------------------------------------------------

st.divider()

st.subheader("📋 Automatic Data Quality Report")

# BEFORE cleaning
before_rows = len(original)
before_columns = len(original.columns)
before_missing = int(original.isna().sum().sum())
before_duplicates = int(original.duplicated().sum())
before_quality = calculate_quality_score(original)

# AFTER cleaning
after_rows = len(cleaned)
after_columns = len(cleaned.columns)
after_missing = int(cleaned.isna().sum().sum())
after_duplicates = int(cleaned.duplicated().sum())
after_quality = calculate_quality_score(cleaned)

# -----------------------------------------------------
# QUALITY SCORE
# -----------------------------------------------------

st.markdown("### 🎯 Data Quality Score")

score_col1, score_col2 = st.columns(2)

with score_col1:
    st.metric(
        "Before Cleaning",
        f"{before_quality:.0f}%"
    )

with score_col2:
    st.metric(
        "After Cleaning",
        f"{after_quality:.0f}%",
        delta=f"{after_quality - before_quality:.0f}%"
    )

# Progress bar
st.progress(
    min(after_quality / 100, 1.0)
)

if after_quality >= 90:
    st.success(
        "🟢 The cleaned dataset has a high data quality score."
    )

elif after_quality >= 70:
    st.warning(
        "🟡 The cleaned dataset has moderate data quality."
    )

else:
    st.error(
        "🔴 The dataset may still need additional cleaning."
    )

# -----------------------------------------------------
# BEFORE VS AFTER
# -----------------------------------------------------

st.markdown("### 📊 Before vs. After")

report = pd.DataFrame({
    "Metric": [
        "Rows",
        "Columns",
        "Missing Cells",
        "Duplicate Rows"
    ],
    "Before": [
        before_rows,
        before_columns,
        before_missing,
        before_duplicates
    ],
    "After": [
        after_rows,
        after_columns,
        after_missing,
        after_duplicates
    ]
})

report["Change"] = (
    report["After"] - report["Before"]
)

st.dataframe(
    report,
    use_container_width=True,
    hide_index=True
)

# -----------------------------------------------------
# CHANGES MADE
# -----------------------------------------------------

st.markdown("### 🧹 Cleaning Operations")

if changes:

    for change in changes:
        st.write("✅ " + change)

else:

    st.info(
        "No cleaning operations were required."
    )

# -----------------------------------------------------
# DATASET SUMMARY
# -----------------------------------------------------

st.markdown("### 📦 Dataset Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:

    st.metric(
        "Rows Removed",
        f"{max(before_rows - after_rows, 0):,}"
    )

with summary_col2:

    st.metric(
        "Missing Values Handled",
        f"{max(before_missing - after_missing, 0):,}"
    )

with summary_col3:

    st.metric(
        "Duplicates Removed",
        f"{max(before_duplicates - after_duplicates, 0):,}"
    )

# -----------------------------------------------------
# FINAL STATUS
# -----------------------------------------------------

st.markdown("### ✅ Final Status")

if (
    after_missing == 0
    and after_duplicates == 0
    and after_quality >= 90
):

    st.success(
        "🎉 Your dataset is clean and ready for analysis."
    )

else:

    st.info(
        "Your dataset has been cleaned, but some issues may remain."
    )

    final_score = calculate_quality_score(
        cleaned
    )

    a, b, c = st.columns(3)

    a.metric(
        "Remaining Missing Cells",
        f"{final_missing:,}"
    )

    b.metric(
        "Remaining Duplicates",
        f"{final_duplicates:,}"
    )

    c.metric(
        "Final Quality Score",
        f"{final_score:.0f}%"
    )

    st.success(
        "Your cleaned dataset is ready to download."
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Personal learning project • Python + Pandas + NumPy + Streamlit + Plotly"
)
