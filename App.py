
import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Cassette & BMS Management System", layout="wide")

DB = "cassette.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cassette (
        Date TEXT,
        CassetteID TEXT PRIMARY KEY,
        BMSVersion TEXT,
        Voltage TEXT,
        Current TEXT,
        Temperature TEXT,
        SOC TEXT,
        SOH TEXT,
        FaultCode TEXT,
        OverallStatus TEXT,
        Remarks TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def load_data():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cassette", conn)
    conn.close()
    return df

def save_record(values):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO cassette
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, values)
    conn.commit()
    conn.close()

st.title("🔋 Cassette & BMS Management System")

tabs = st.tabs(["Add Record", "Database", "Dashboard"])

with tabs[0]:
    st.subheader("Add Record")
    with st.form("record_form"):
        date = st.text_input("Date", value=str(datetime.now().date()))
        cid = st.text_input("Cassette ID")
        bms = st.text_input("BMS Version")
        voltage = st.text_input("Voltage")
        current = st.text_input("Current")
        temp = st.text_input("Temperature")
        soc = st.text_input("SOC")
        soh = st.text_input("SOH")
        fault = st.text_input("Fault Code")
        status = st.selectbox("Overall Status", ["PASS","FAIL","OBSERVATION"])
        remarks = st.text_input("Remarks")

        if st.form_submit_button("Save"):
            save_record((date,cid,bms,voltage,current,temp,soc,soh,fault,status,remarks))
            st.success("Saved")

with tabs[1]:
    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        csv = df.to_csv(index=False).encode()
        st.download_button("Export CSV", csv, "cassette_data.csv", "text/csv")

with tabs[2]:
    df = load_data()
    if df.empty:
        st.warning("No data available")
    else:
        c1,c2,c3 = st.columns(3)
        c1.metric("Total Records", len(df))
        c2.metric("PASS", (df["OverallStatus"]=="PASS").sum())
        c3.metric("FAIL", (df["OverallStatus"]=="FAIL").sum())

        counts = df["OverallStatus"].value_counts()
        fig, ax = plt.subplots()
        ax.bar(counts.index, counts.values)
        st.pyplot(fig)
