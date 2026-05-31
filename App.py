import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="Cassette Entry System",
    layout="wide"
)

DB = "cassette.db"

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
# DB CONNECTION
# ==========================

def get_conn():
    return sqlite3.connect(DB)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS cassette (
        Date TEXT,
        "Battery Cassette ID" TEXT,
        "BMS Software Version" TEXT,
        Voltage TEXT,
        Current TEXT,
        Temperature TEXT,
        "SOC %" TEXT,
        "SOH %" TEXT,
        "Cycle Count" TEXT,
        "Distance Covered Km" TEXT,
        "Issue-Free Km" TEXT,
        "Root Cause" TEXT,
        "Issue Status" TEXT,
        "Overall Status" TEXT,
        "Fault Code" TEXT,
        "Battery Health" TEXT,
        "Over Heating" TEXT,
        "Cell Imbalance" TEXT,
        "Connector Issue" TEXT,
        "Charging Issue" TEXT,
        "Discharging Issue" TEXT,
        Remarks TEXT,
        "Application Area" TEXT,
        "Current Location" TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ==========================
# LOAD DATA
# ==========================

def load_data():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cassette", conn)
    conn.close()
    return df

# ==========================
# SAVE RECORD
# ==========================

def save_record(data):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO cassette VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data["Date"],
        data["Battery Cassette ID"],
        data["BMS Software Version"],
        data["Voltage"],
        data["Current"],
        data["Temperature"],
        data["SOC %"],
        data["SOH %"],
        data["Cycle Count"],
        data["Distance Covered Km"],
        data["Issue-Free Km"],
        data["Root Cause"],
        data["Issue Status"],
        data["Overall Status"],
        data["Fault Code"],
        data["Battery Health"],
        data["Over Heating"],
        data["Cell Imbalance"],
        data["Connector Issue"],
        data["Charging Issue"],
        data["Discharging Issue"],
        data["Remarks"],
        data["Application Area"],
        data["Current Location"]
    ))

    conn.commit()
    conn.close()

# ==========================
# DELETE RECORD
# ==========================

def delete_record(cassette_id):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM cassette WHERE "Battery Cassette ID"=?
    """, (cassette_id,))

    conn.commit()
    conn.close()

# ==========================
# UI
# ==========================

st.title("🔋 Cassette Entry System (SQLite Version)")

tab1, tab2, tab3 = st.tabs([
    "Add Entry",
    "Database",
    "Analytics"
])

# ==========================
# TAB 1
# ==========================

with tab1:

    st.subheader("Add New Battery Record")

    with st.form("form"):

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

        submit = st.form_submit_button("💾 Save Record")

        if submit:

            if data["Battery Cassette ID"].strip() == "":
                st.error("Battery Cassette ID Required")

            else:
                save_record(data)
                st.success("Saved Successfully")

# ==========================
# TAB 2
# ==========================

with tab2:

    st.subheader("Database Records")

    df = load_data()

    search = st.text_input("Search")

    if search:
        df = df[df.astype(str).apply(lambda row: row.str.contains(search, case=False).any(), axis=1)]

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "cassette_export.csv",
        "text/csv"
    )

    st.subheader("Delete Record")

    if len(df) > 0:

        cassette = st.selectbox(
            "Select ID",
            df["Battery Cassette ID"].astype(str).unique()
        )

        if st.button("Delete"):
            delete_record(cassette)
            st.success("Deleted")
            st.rerun()

# ==========================
# TAB 3
# ==========================

with tab3:

    st.subheader("Analytics")

    df = load_data()

    if df.empty:
        st.warning("No Data")
    else:

        col = st.selectbox("Select Parameter", df.columns)

        counts = df[col].astype(str).value_counts()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(counts.index, counts.values, color="#00BFFF")

        plt.xticks(rotation=45)

        st.pyplot(fig)

        st.write("Total Records:", len(df))
