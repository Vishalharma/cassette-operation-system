import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ==========================
# CONFIG
# ==========================

st.set_page_config(page_title="Cassette Operation System", layout="wide")

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cassette.db")

# ==========================
# DB CONNECTION
# ==========================

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

# ==========================
# INIT DB
# ==========================

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cassette (
        Date TEXT,
        "Battery Cassette ID" TEXT PRIMARY KEY,
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
# DATA COLUMNS
# ==========================

columns = [
    "Date","Battery Cassette ID","BMS Software Version","Voltage","Current",
    "Temperature","SOC %","SOH %","Cycle Count","Distance Covered Km",
    "Issue-Free Km","Root Cause","Issue Status","Overall Status","Fault Code",
    "Battery Health","Over Heating","Cell Imbalance","Connector Issue",
    "Charging Issue","Discharging Issue","Remarks","Application Area",
    "Current Location"
]

# ==========================
# DB FUNCTIONS
# ==========================

def load_data():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cassette", conn)
    conn.close()
    return df


def save_record(data):
    conn = get_conn()
    cur = conn.cursor()

    cols = ", ".join([f'"{c}"' for c in columns])
    placeholders = ", ".join(["?"] * len(columns))
    values = tuple(data.get(c, "") for c in columns)

    cur.execute(f"""
    INSERT OR REPLACE INTO cassette ({cols})
    VALUES ({placeholders})
    """, values)

    conn.commit()
    conn.close()


def delete_record(cid):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute('DELETE FROM cassette WHERE "Battery Cassette ID"=?', (cid,))
    conn.commit()
    conn.close()

# ==========================
# UI
# ==========================

st.title("🔋 Cassette Operation System")

tab1, tab2, tab3 = st.tabs([
    "➕ Add Entry",
    "📊 Database",
    "📈 Analytics"
])

# ==========================
# TAB 1 - ADD DATA
# ==========================

with tab1:

    st.subheader("➕ Add New Record")

    with st.form("add_form"):

        data = {}
        c1, c2 = st.columns(2)

        for i, f in enumerate(columns):

            target = c1 if i % 2 == 0 else c2

            with target:
                if f == "Date":
                    data[f] = st.text_input(f, value=str(datetime.now().date()))
                else:
                    data[f] = st.text_input(f)

        submit = st.form_submit_button("💾 Save Record")

        if submit:
            if data["Battery Cassette ID"].strip() == "":
                st.error("Battery Cassette ID is required")
            else:
                save_record(data)
                st.success("Record saved successfully")

# ==========================
# TAB 2 - DATABASE VIEW
# ==========================

with tab2:

    st.subheader("📊 All Records")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:

        st.markdown("### 🗑 Delete Record")

        cid = st.selectbox("Select Cassette ID", df["Battery Cassette ID"].astype(str))

        if st.button("Delete"):
            delete_record(cid)
            st.success("Record deleted")
            st.rerun()

# ==========================
# TAB 3 - ANALYTICS
# ==========================

with tab3:

    st.subheader("📈 Analytics Dashboard")

    df = load_data()

    if df.empty:
        st.warning("No data available")
    else:
        col = st.selectbox("Select Parameter", df.columns)

        counts = df[col].astype(str).value_counts()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(counts.index, counts.values, color="#00BFFF")

        plt.xticks(rotation=45)

        st.pyplot(fig)

        st.write("Total Records:", len(df))
