import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

st.set_page_config(page_title="Cassette Operation System", layout="wide")

DB = "cassette.db"


def conn():
    return sqlite3.connect(DB, check_same_thread=False)


def hpw(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    c = conn()
    cur = c.cursor()

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
        cassette_id TEXT PRIMARY KEY,
        bms_version TEXT,
        voltage TEXT,
        current TEXT,
        temperature TEXT,
        soc TEXT,
        soh TEXT,
        cycle_count TEXT,
        fault_code TEXT,
        location TEXT,
        remarks TEXT
    )
    """)

    cur.execute("SELECT COUNT(*) FROM users WHERE username='admin'")

    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users VALUES(?,?,?,?)",
            ("admin", hpw("admin123"), "Admin", "Active")
        )

    c.commit()
    c.close()


init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

# ---------------- LOGIN ----------------

if not st.session_state.logged_in:

    st.title("🔐 Cassette Operation System Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        c = conn()
        cur = c.cursor()

        cur.execute(
            """
            SELECT role
            FROM users
            WHERE username=?
            AND password=?
            AND status='Active'
            """,
            (username, hpw(password))
        )

        user = cur.fetchone()

        status = "Success" if user else "Failed"

        cur.execute(
            """
            INSERT INTO login_history
            (username, login_time, status)
            VALUES (?,?,?)
            """,
            (
                username,
                str(datetime.now()),
                status
            )
        )

        c.commit()
        c.close()

        if user:
            st.session_state.logged_in = True
            st.session_state.role = user[0]
            st.rerun()
        else:
            st.error("Invalid Username or Password")

    st.stop()

# ---------------- MAIN APP ----------------

st.title("🔋 Cassette Operation System")

col1, col2 = st.columns([8, 2])

with col2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = ""
        st.rerun()

tabs = st.tabs(
    [
        "Add Record",
        "Database",
        "Edit",
        "Analytics",
        "Users"
    ]
)

# ---------------- ADD RECORD ----------------

with tabs[0]:

    st.subheader("Add Cassette Record")

    with st.form("add_record"):

        cassette_id = st.text_input("Cassette ID")
        bms_version = st.text_input("BMS Version")
        voltage = st.text_input("Voltage")
        current = st.text_input("Current")
        temperature = st.text_input("Temperature")
        soc = st.text_input("SOC")
        soh = st.text_input("SOH")
        cycle_count = st.text_input("Cycle Count")
        fault_code = st.text_input("Fault Code")
        location = st.text_input("Location")
        remarks = st.text_input("Remarks")

        submit = st.form_submit_button("Save Record")

        if submit:

            c = conn()

            c.execute(
                """
                INSERT OR REPLACE INTO cassette
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    str(datetime.now().date()),
                    cassette_id,
                    bms_version,
                    voltage,
                    current,
                    temperature,
                    soc,
                    soh,
                    cycle_count,
                    fault_code,
                    location,
                    remarks
                )
            )

            c.commit()
            c.close()

            st.success("Record Saved Successfully")

# ---------------- DATABASE ----------------

with tabs[1]:

    st.subheader("Cassette Database")

    c = conn()
    df = pd.read_sql_query("SELECT * FROM cassette", c)
    c.close()

    search = st.text_input("Search Cassette ID")

    if search:
        df = df[
            df["cassette_id"]
            .astype(str)
            .str.contains(search, case=False, na=False)
        ]

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Export CSV",
        df.to_csv(index=False).encode(),
        "cassette.csv",
        "text/csv"
    )

    if not df.empty:

        selected = st.selectbox(
            "Select Cassette",
            df["cassette_id"]
        )

        row = df[df["cassette_id"] == selected].iloc[0]

        st.write(row)

        if st.button("Delete Cassette"):

            c = conn()

            c.execute(
                "DELETE FROM cassette WHERE cassette_id=?",
                (selected,)
            )

            c.commit()
            c.close()

            st.success("Deleted Successfully")
            st.rerun()

# ---------------- EDIT ----------------

with tabs[2]:

    st.subheader("Edit Record")

    c = conn()
    df = pd.read_sql_query("SELECT * FROM cassette", c)
    c.close()

    if not df.empty:

        selected = st.selectbox(
            "Select Cassette To Edit",
            df["cassette_id"]
        )

        row = df[df["cassette_id"] == selected].iloc[0]

        voltage = st.text_input(
            "Voltage",
            str(row["voltage"])
        )

        current = st.text_input(
            "Current",
            str(row["current"])
        )

        if st.button("Update Record"):

            c = conn()

            c.execute(
                """
                UPDATE cassette
                SET voltage=?,
                    current=?
                WHERE cassette_id=?
                """,
                (
                    voltage,
                    current,
                    selected
                )
            )

            c.commit()
            c.close()

            st.success("Record Updated")

# ---------------- ANALYTICS ----------------

with tabs[3]:

    st.subheader("Analytics")

    c = conn()
    df = pd.read_sql_query("SELECT * FROM cassette", c)
    c.close()

    st.metric("Total Records", len(df))

    if not df.empty:

        st.subheader("Fault Code Distribution")

        fault_data = (
            df["fault_code"]
            .astype(str)
            .value_counts()
        )

        st.bar_chart(fault_data)

# ---------------- USERS ----------------

with tabs[4]:

    if st.session_state.role == "Admin":

        st.subheader("User Management")

        username = st.text_input("New Username")

        password = st.text_input(
            "New Password",
            type="password"
        )

        role = st.selectbox(
            "Role",
            [
                "Admin",
                "Engineer",
                "Operator",
                "Viewer"
            ]
        )

        status = st.selectbox(
            "Status",
            [
                "Active",
                "Inactive"
            ]
        )

        if st.button("Save User"):

            c = conn()

            c.execute(
                """
                INSERT OR REPLACE INTO users
                VALUES(?,?,?,?)
                """,
                (
                    username,
                    hpw(password),
                    role,
                    status
                )
            )

            c.commit()
            c.close()

            st.success("User Saved")

        c = conn()

        users = pd.read_sql_query(
            """
            SELECT username,
                   role,
                   status
            FROM users
            """,
            c
        )

        logs = pd.read_sql_query(
            """
            SELECT *
            FROM login_history
            ORDER BY id DESC
            """,
            c
        )

        c.close()

        st.subheader("Users")

        st.dataframe(
            users,
            use_container_width=True
        )

        st.subheader("Login History")

        st.dataframe(
            logs,
            use_container_width=True
        )

    else:

        st.warning(
            "Only Admin can access User Management."
        )
