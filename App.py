
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib

st.set_page_config(page_title="Cassette Operation System", layout="wide")

DB = "cassette.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS login_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        login_time TEXT,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cassette(
        Date TEXT,
        "Battery Cassette ID" TEXT PRIMARY KEY,
        Voltage TEXT,
        Current TEXT,
        Temperature TEXT,
        "SOC %" TEXT,
        "SOH %" TEXT,
        "Fault Code" TEXT,
        "Current Location" TEXT,
        Remarks TEXT
    )
    """)

    cur.execute(
        "INSERT OR IGNORE INTO users VALUES(?,?,?,?)",
        ("admin", hash_pw("admin123"), "Admin", "Active")
    )

    conn.commit()
    conn.close()

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_conn()
        q = pd.read_sql_query(
            "SELECT * FROM users WHERE username=? AND password=? AND status='Active'",
            conn,
            params=(user, hash_pw(pwd))
        )

        conn.execute(
            "INSERT INTO login_history(username,login_time,status) VALUES(?,?,?)",
            (user, str(datetime.now()), "Success" if len(q) else "Failed")
        )
        conn.commit()
        conn.close()

        if len(q):
            st.session_state.logged_in = True
            st.session_state.role = q.iloc[0]["role"]
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid Login")

    st.stop()

st.title("🔋 Cassette Operation System")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["➕ Add", "📊 Database", "✏ Edit", "📈 Analytics", "👤 Users"]
)

with tab1:
    with st.form("add_form"):
        cid = st.text_input("Battery Cassette ID")
        voltage = st.text_input("Voltage")
        current = st.text_input("Current")
        temp = st.text_input("Temperature")
        soc = st.text_input("SOC %")
        soh = st.text_input("SOH %")
        fault = st.text_input("Fault Code")
        loc = st.text_input("Current Location")
        remarks = st.text_input("Remarks")

        if st.form_submit_button("Save"):
            conn = get_conn()
            conn.execute(
                'INSERT OR REPLACE INTO cassette VALUES(?,?,?,?,?,?,?,?,?,?)',
                (
                    str(datetime.now().date()),
                    cid, voltage, current, temp,
                    soc, soh, fault, loc, remarks
                )
            )
            conn.commit()
            conn.close()
            st.success("Saved")

with tab2:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cassette", conn)
    conn.close()

    search = st.text_input("🔍 Search Cassette ID")

    if search:
        df = df[df["Battery Cassette ID"].astype(str).str.contains(search, case=False, na=False)]

    st.dataframe(df, use_container_width=True)

    if not df.empty:
        selected = st.selectbox("Select Cassette", df["Battery Cassette ID"])

        row = df[df["Battery Cassette ID"] == selected].iloc[0]

        c1, c2, c3 = st.columns(3)
        c1.metric("Voltage", row["Voltage"])
        c2.metric("SOC", row["SOC %"])
        c3.metric("SOH", row["SOH %"])

        if st.button("Delete Selected"):
            conn = get_conn()
            conn.execute('DELETE FROM cassette WHERE "Battery Cassette ID"=?', (selected,))
            conn.commit()
            conn.close()
            st.rerun()

    st.download_button(
        "📥 Export CSV",
        df.to_csv(index=False).encode(),
        "cassette_records.csv",
        "text/csv"
    )

with tab3:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cassette", conn)
    conn.close()

    if not df.empty:
        cid = st.selectbox("Edit Cassette", df["Battery Cassette ID"])
        row = df[df["Battery Cassette ID"] == cid].iloc[0]

        voltage = st.text_input("Voltage", row["Voltage"])
        current = st.text_input("Current", row["Current"])

        if st.button("Update"):
            conn = get_conn()
            conn.execute(
                'UPDATE cassette SET Voltage=?, Current=? WHERE "Battery Cassette ID"=?',
                (voltage, current, cid)
            )
            conn.commit()
            conn.close()
            st.success("Updated")

with tab4:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cassette", conn)
    conn.close()

    st.write("Total Records:", len(df))

    if not df.empty:
        st.bar_chart(df["Fault Code"].astype(str).value_counts())

with tab5:
    if st.session_state.role == "Admin":
        st.subheader("User Management")

        uname = st.text_input("Username")
        upass = st.text_input("Password")
        role = st.selectbox("Role", ["Admin", "Engineer", "Operator", "Viewer"])
        status = st.selectbox("Status", ["Active", "Inactive"])

        if st.button("Create User"):
            conn = get_conn()
            conn.execute(
                "INSERT OR REPLACE INTO users VALUES(?,?,?,?)",
                (uname, hash_pw(upass), role, status)
            )
            conn.commit()
            conn.close()
            st.success("User Saved")

        conn = get_conn()
        users = pd.read_sql_query("SELECT username,role,status FROM users", conn)
        hist = pd.read_sql_query("SELECT * FROM login_history ORDER BY id DESC", conn)
        conn.close()

        st.subheader("Users")
        st.dataframe(users, use_container_width=True)

        st.subheader("Login History")
        st.dataframe(hist, use_container_width=True)
    else:
        st.warning("Admin only")
