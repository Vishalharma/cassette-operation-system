import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="Cassette Entry System",
    layout="wide"
)

FILE = "cassette_database.csv"

columns = [
    "Date",
    "Battery Cassette ID",
    "BMS Software Version",
    "Voltage",
    "Current",
    "Temperature",
    "SOC %",
    "SOH %",
    "Cycle Count",
    "Distance Covered Km",
    "Issue-Free Km",
    "Root Cause",
    "Issue Status",
    "Overall Status",
    "Fault Code",
    "Battery Health",
    "Over Heating",
    "Cell Imbalance",
    "Connector Issue",
    "Charging Issue",
    "Discharging Issue",
    "Remarks",
    "Application Area",
    "Current Location"
]

# ==========================
# SAFE FILE INIT
# ==========================

if not os.path.exists(FILE):
    pd.DataFrame(columns=columns).to_csv(FILE, index=False)

# ==========================
# SAFE LOAD
# ==========================

def load_data():
    if os.path.exists(FILE):
        try:
            df = pd.read_csv(FILE)
            return df
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# ==========================
# SAVE RECORD
# ==========================

def save_record(data):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(FILE, index=False)

# ==========================
# DELETE RECORD
# ==========================

def delete_record(cassette_id):
    df = load_data()

    if "Battery Cassette ID" not in df.columns:
        return

    df = df[df["Battery Cassette ID"].astype(str) != str(cassette_id)]
    df.to_csv(FILE, index=False)

# ==========================
# TITLE
# ==========================

st.title("🔋 Cassette Entry System")

tab1, tab2, tab3 = st.tabs([
    "Add Entry",
    "Database",
    "Analytics"
])

# ==========================
# TAB 1 - ADD ENTRY
# ==========================

with tab1:

    st.subheader("Add New Battery Record")

    with st.form("entry_form"):

        data = {}

        col1, col2 = st.columns(2)

        for i, field in enumerate(columns):

            target = col1 if i % 2 == 0 else col2

            with target:

                if field == "Date":
                    data[field] = st.text_input(
                        field,
                        value=datetime.now().strftime("%d-%m-%Y")
                    )

                elif field == "Issue Status":
                    data[field] = st.selectbox(
                        field,
                        ["GREEN", "YELLOW", "RED", "WHITE"]
                    )

                elif field == "Battery Health":
                    data[field] = st.selectbox(
                        field,
                        ["GOOD", "AVERAGE", "CRITICAL"]
                    )

                else:
                    data[field] = st.text_input(field)

        submitted = st.form_submit_button("💾 Save Record")

        if submitted:

            if data["Battery Cassette ID"].strip() == "":
                st.error("Battery Cassette ID Required")

            else:
                save_record(data)
                st.success("Record Saved Successfully")

# ==========================
# TAB 2 - DATABASE
# ==========================

with tab2:

    st.subheader("Database Records")

    df = load_data()

    search = st.text_input("Search Any Value")

    if search:

        mask = df.astype(str).apply(
            lambda row: row.str.contains(search, case=False).any(),
            axis=1
        )

        df = df[mask]

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "📥 Download CSV",
        data=df.to_csv(index=False),
        file_name="cassette_export.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("Delete Record")

    if len(df) > 0:

        cassette = st.selectbox(
            "Select Cassette ID",
            df["Battery Cassette ID"].astype(str).unique()
        )

        if st.button("🗑 Delete"):

            delete_record(cassette)
            st.success(f"{cassette} deleted successfully")
            st.rerun()

# ==========================
# TAB 3 - ANALYTICS
# ==========================

with tab3:

    st.subheader("Analytics Dashboard")

    df = load_data()

    if df.empty:
        st.warning("No Data Available")

    else:

        graph_column = st.selectbox(
            "Select Parameter",
            df.columns
        )

        counts = df[graph_column].astype(str).value_counts()

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.bar(counts.index, counts.values, color="#00BFFF")
        ax.set_title(graph_column)

        plt.xticks(rotation=45)

        st.pyplot(fig)

        st.subheader("Statistics")

        st.write(f"Total Records: {len(df)}")

        if "Issue Status" in df.columns:
            st.write(df["Issue Status"].value_counts())
