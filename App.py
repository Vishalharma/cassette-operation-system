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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "cassette.db")

# ==========================
# SESSION STATE
# ==========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

# ==========================
# DB INIT (FIXED SAFE VERSION)
# ==========================

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)

    # CASSETTE TABLE
    cursor.execute("""
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

    # SAFE ADMIN INSERT (FIXED)
    cursor.execute("""
    SELECT COUNT(*) FROM users WHERE username='admin'
    """)
    exists = cursor.fetchone()[0]

    if exists == 0:
        cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, ("admin", "admin123", "admin"))

    conn.commit()
    conn.close()

init_db()

# ==========================
# AUTH
# ==========================

def authenticate(username, password):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role FROM users
    WHERE username=? AND password=?
    """, (username, password))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

# ==========================
# DATA COLUMNS
# ==========================

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
# DB FUNCTIONS
# ==========================

def load_data():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cassette", conn)
    conn.close()
    return df

def save_record(data):
    conn = get_conn()
    cursor = conn.cursor()

    cols = ", ".join([f'"{c}"' for c in columns])
    placeholders = ", ".join(["?"] * len(columns))
    values = tuple(data.get(c, "") for c in columns)

    cursor.execute(f"""
    INSERT OR REPLACE INTO cassette ({cols})
    VALUES ({placeholders})
    """, values)

    conn.commit()
    conn.close()

def delete_record(cid):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM cassette WHERE "Battery Cassette ID"=?
    """, (cid,))

    conn.commit()
    conn.close()

# ==========================
# LOGIN PAGE
# ==========================

def login_page():
    st.title("🔐 Cassette System Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = authenticate(username, password)

        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.username = username
            st.success(f"Welcome {username} ({role})")
            st.rerun()
        else:
            st.error("Invalid username or password")

# ==========================
# LOGOUT
# ==========================

def logout():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

# ==========================
# BLOCK IF NOT LOGGED IN
# ==========================

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ==========================
# UI HEADER
# ==========================

st.title("🔋 Cassette Operation System")

st.sidebar.write(f"👤 User: {st.session_state.username}")
st.sidebar.write(f"🔐 Role: {st.session_state.role}")

logout()

tab1, tab2, tab3 = st.tabs(["➕ Add Entry", "📊 Database", "📈 Analytics"])

# ==========================
# TAB 1 (ADMIN ONLY)
# ==========================

with tab1:

    st.subheader("Add New Record")

    if st.session_state.role != "admin":
        st.warning("Only admin can add/edit records.")
    else:

        with st.form("form"):

            data = {}
            c1, c2 = st.columns(2)

            for i, f in enumerate(columns):

                target = c1 if i % 2 == 0 else c2

                with target:

                    if f == "Date":
                        data[f] = st.text_input(f, value=datetime.now().strftime("%d-%m-%Y"))

                    elif f == "Issue Status":
                        data[f] = st.selectbox(f, ["GREEN", "YELLOW", "RED", "WHITE"])

                    elif f == "Battery Health":
                        data[f] = st.selectbox(f, ["GOOD", "AVERAGE", "CRITICAL"])

                    else:
                        data[f] = st.text_input(f)

            submit = st.form_submit_button("💾 Save Record")

            if submit:
                if data["Battery Cassette ID"].strip() == "":
                    st.error("Battery Cassette ID Required")
                else:
                    save_record(data)
                    st.success("Saved Successfully")

# ==========================
# TAB 2 (VIEW ALL)
# ==========================

with tab2:

    df = load_data()

    search = st.text_input("Search Data")

    if search:
        df = df[df.astype(str).apply(lambda r: r.str.contains(search, case=False).any(), axis=1)]

    st.dataframe(df, use_container_width=True)

    st.download_button("⬇ Download CSV", df.to_csv(index=False), "cassette_data.csv", "text/csv")

    if st.session_state.role == "admin":

        st.subheader("🗑 Delete Record")

        if len(df) > 0:

            cid = st.selectbox("Select Cassette ID", df["Battery Cassette ID"].astype(str).unique())

            if st.button("Delete"):
                delete_record(cid)
                st.success("Deleted Successfully")
                st.rerun()

    else:
        st.info("Only admin can delete records.")

# ==========================
# TAB 3 (ANALYTICS)
# ==========================

with tab3:

    df = load_data()

    if df.empty:
        st.warning("No Data Available")
    else:

        col = st.selectbox("Select Parameter", df.columns)

        counts = df[col].astype(str).value_counts()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(counts.index, counts.values, color="#00BFFF")

        plt.xticks(rotation=45)

        st.pyplot(fig)

        st.write("Total Records:", len(df))
