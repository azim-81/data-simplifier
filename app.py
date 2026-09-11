import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Simplifier", page_icon="📊", layout="wide")

st.title("Data Simplifier")
st.write("A small tool I made to clean a spreadsheet and get a quick look at the data.")

with st.sidebar:
    st.header("Start here")
    uploaded = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    st.caption("Tip: You can try the sample file included with this project.")

if uploaded is None:
    st.info("Upload a CSV or Excel file to begin.")
    st.subheader("What this tool does")
    st.write(
        "It checks a dataset for common problems such as missing values, "
        "duplicate rows and inconsistent column names. You can then clean the "
        "data and explore a few basic charts."
    )
    st.markdown("**Built with:** Python · Pandas · Streamlit · Plotly")
    st.stop()

try:
    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"I couldn't read this file: {e}")
    st.stop()

if df.empty:
    st.warning("The file was read, but it does not contain any rows.")
    st.stop()

original = df.copy()

tab1, tab2, tab3 = st.tabs(["Overview", "Clean data", "Explore"])

with tab1:
    st.subheader("Overview")
    missing = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())

    a, b, c, d = st.columns(4)
    a.metric("Rows", len(df))
    b.metric("Columns", len(df.columns))
    c.metric("Missing cells", missing)
    d.metric("Duplicate rows", duplicates)

    st.subheader("Columns")
    profile = pd.DataFrame({
        "Column": df.columns,
        "Type": [str(x) for x in df.dtypes],
        "Missing": df.isna().sum().values,
        "Unique": [df[x].nunique(dropna=True) for x in df.columns],
    })
    st.dataframe(profile, use_container_width=True, hide_index=True)

    st.subheader("First few rows")
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Clean data")
    st.write("Choose the changes you want to make. The original upload is not changed.")

    remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
    tidy_names = st.checkbox("Tidy column names", value=True)
    remove_empty = st.checkbox("Remove completely empty rows and columns", value=True)

    if st.button("Clean my data", type="primary"):
        cleaned = original.copy()
        changes = []

        if remove_empty:
            before_rows, before_cols = cleaned.shape
            cleaned = cleaned.dropna(axis=0, how="all")
            cleaned = cleaned.dropna(axis=1, how="all")
            if cleaned.shape != (before_rows, before_cols):
                changes.append(
                    f"Removed {before_rows - cleaned.shape[0]} empty rows "
                    f"and {before_cols - cleaned.shape[1]} empty columns."
                )

        if tidy_names:
            old_names = list(cleaned.columns)
            new_names = (
                cleaned.columns.astype(str)
                .str.strip()
                .str.lower()
                .str.replace(r"\s+", "_", regex=True)
                .str.replace(r"[^a-z0-9_]", "", regex=True)
            )
            cleaned.columns = new_names
            changed = sum(a != b for a, b in zip(old_names, new_names))
            if changed:
                changes.append(f"Tidied {changed} column name(s).")

        if remove_duplicates:
            before = len(cleaned)
            cleaned = cleaned.drop_duplicates()
            removed = before - len(cleaned)
            if removed:
                changes.append(f"Removed {removed} duplicate row(s).")

        st.session_state["cleaned"] = cleaned
        st.session_state["changes"] = changes

    if "cleaned" in st.session_state:
        cleaned = st.session_state["cleaned"]
        changes = st.session_state["changes"]

        st.success("Cleaning finished.")

        st.write("### What changed")
        if changes:
            for item in changes:
                st.write("• " + item)
        else:
            st.write("No changes were needed with the selected options.")

        left, right = st.columns(2)
        with left:
            st.write("**Before**")
            st.write(f"{len(original):,} rows × {len(original.columns):,} columns")
        with right:
            st.write("**After**")
            st.write(f"{len(cleaned):,} rows × {len(cleaned.columns):,} columns")

        st.write("### Cleaned data")
        st.dataframe(cleaned.head(50), use_container_width=True, hide_index=True)

        st.download_button(
            "Download cleaned CSV",
            cleaned.to_csv(index=False).encode("utf-8"),
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

with tab3:
    st.subheader("Explore the data")
    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = df.select_dtypes(exclude="number").columns.tolist()

    if numeric:
        chosen = st.selectbox("Choose a numeric column", numeric)
        fig = px.histogram(df, x=chosen, title=f"Distribution of {chosen}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric columns were found for a histogram.")

    if categorical:
        chosen_cat = st.selectbox("Choose a category column", categorical)
        counts = df[chosen_cat].astype(str).value_counts().head(15).reset_index()
        counts.columns = [chosen_cat, "Count"]
        fig2 = px.bar(counts, x=chosen_cat, y="Count", title=f"Most common values in {chosen_cat}")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No text/category columns were found for a category chart.")

st.divider()
st.caption("Personal learning project • Python + Pandas + Streamlit + Plotly")
