import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="Cassette Operation System",
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

    # CASSETTE TABLE
    cursor.execute("""
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

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    # LOGIN HISTORY
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        login_time TEXT
    )
    """)

    # DEFAULT ADMIN
    cursor.execute("""
    INSERT OR IGNORE INTO users(username,password,role,active)
    VALUES ('admin','admin123','Admin',1)
    """)

    conn.commit()
    conn.close()

init_db()

# ==========================
# AUTH
# ==========================

def login_user(username, password):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, role, active
    FROM users
    WHERE username=? AND password=?
    """, (username, password))

    user = cursor.fetchone()
    conn.close()
    return user

# ==========================
# DATA FUNCTIONS
# ==========================

def load_data():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cassette", conn)
    conn.close()
    return df

def save_record(data):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO cassette VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, tuple(data.values()))

    conn.commit()
    conn.close()

def delete_record(cassette_id):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM cassette WHERE "Battery Cassette ID"=?
    """, (cassette_id,))

    conn.commit()
    conn.close()

# ==========================
# LOGIN SYSTEM
# ==========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 Cassette Operation System Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = login_user(username, password)

        if user:

            if user[2] == 0:
                st.error("User Inactive")
                st.stop()

            st.session_state.logged_in = True
            st.session_state.username = user[0]
            st.session_state.role = user[1]

            conn = get_conn()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO login_history(username, login_time)
            VALUES (?,?)
            """, (user[0], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            conn.commit()
            conn.close()

            st.rerun()

        else:
            st.error("Invalid Login")

    st.stop()

# ==========================
# HEADER
# ==========================

st.title("🔋 Cassette Operation System")

col1, col2 = st.columns([8,1])

with col2:
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

st.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")

# ==========================
# TABS
# ==========================

tab1, tab2, tab3 = st.tabs(["Add Entry", "Database", "Analytics"])

# ==========================
# TAB 1 - ADD ENTRY
# ==========================

with tab1:

    st.subheader("Add New Record")

    with st.form("form"):

        data = {}

        col1, col2 = st.columns(2)

        for i, field in enumerate(columns):

            target = col1 if i % 2 == 0 else col2

            with target:

                if field == "Date":
                    data[field] = st.text_input(field, value=datetime.now().strftime("%d-%m-%Y"))

                elif field == "Issue Status":
                    data[field] = st.selectbox(field, ["GREEN","YELLOW","RED","WHITE"])

                elif field == "Battery Health":
                    data[field] = st.selectbox(field, ["GOOD","AVERAGE","CRITICAL"])

                else:
                    data[field] = st.text_input(field)

        submit = st.form_submit_button("Save")

        if submit:
            if data["Battery Cassette ID"] == "":
                st.error("Cassette ID required")
            else:
                save_record(data)
                st.success("Saved Successfully")

# ==========================
# TAB 2 - DATABASE
# ==========================

with tab2:

    df = load_data()

    search = st.text_input("Search")

    if search:
        df = df[df.astype(str).apply(lambda r: r.str.contains(search, case=False).any(), axis=1)]

    st.dataframe(df, use_container_width=True)

    st.download_button("Download CSV", df.to_csv(index=False), "data.csv", "text/csv")

    st.subheader("Delete Record")

    if st.session_state.role == "Admin":

        if len(df) > 0:

            cid = st.selectbox("Select ID", df["Battery Cassette ID"].astype(str).unique())

            if st.button("Delete"):
                delete_record(cid)
                st.success("Deleted")
                st.rerun()

    else:
        st.warning("Only Admin can delete records")

# ==========================
# TAB 3 - ANALYTICS
# ==========================

with tab3:

    df = load_data()

    if df.empty:
        st.warning("No Data")
    else:

        col = st.selectbox("Select Parameter", df.columns)

        counts = df[col].astype(str).value_counts()

        fig, ax = plt.subplots()
        ax.bar(counts.index, counts.values)

        st.pyplot(fig)

        st.write("Total Records:", len(df))Records:", len(df))
