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
# DB CONNECTION
# ==========================

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

# ==========================
# INIT DB
# ==========================

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    # cassette table
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

    # users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)

    # default admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES ('admin','admin123','admin')")

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
    SELECT role FROM users WHERE username=? AND password=?
    """, (username, password))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

# ==========================
# USER FUNCTIONS
# ==========================

def get_users():
    conn = get_conn()
    df = pd.read_sql_query("SELECT username, role FROM users", conn)
    conn.close()
    return df


def add_user(username, password, role):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO users VALUES (?,?,?)
    """, (username, password, role))

    conn.commit()
    conn.close()


def delete_user(username):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()


def update_user(old_username, new_username, password, role):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET username=?, password=?, role=?
    WHERE username=?
    """, (new_username, password, role, old_username))

    conn.commit()
    conn.close()

# ==========================
# DATA
# ==========================

columns = [
    "Date","Battery Cassette ID","BMS Software Version","Voltage","Current",
    "Temperature","SOC %","SOH %","Cycle Count","Distance Covered Km",
    "Issue-Free Km","Root Cause","Issue Status","Overall Status","Fault Code",
    "Battery Health","Over Heating","Cell Imbalance","Connector Issue",
    "Charging Issue","Discharging Issue","Remarks","Application Area",
    "Current Location"
]

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

    cursor.execute('DELETE FROM cassette WHERE "Battery Cassette ID"=?', (cid,))
    conn.commit()
    conn.close()

# ==========================
# LOGIN
# ==========================

def login():
    st.title("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        role = authenticate(u, p)

        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.username = u
            st.rerun()
        else:
            st.error("Invalid login")

# ==========================
# LOGOUT
# ==========================

def logout():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ==========================
# LOGIN CHECK
# ==========================

if not st.session_state.logged_in:
    login()
    st.stop()

# ==========================
# UI HEADER
# ==========================

st.title("🔋 Cassette Operation System")

st.sidebar.write(f"👤 {st.session_state.username}")
st.sidebar.write(f"🔐 {st.session_state.role}")

logout()

# ==========================
# TABS (FIXED)
# ==========================

tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add Entry",
    "📊 Database",
    "📈 Analytics",
    "👥 User Management"
])

# ==========================
# TAB 1 - ADD
# ==========================

with tab1:

    st.subheader("Add Entry")

    if st.session_state.role != "admin":
        st.warning("Only admin can add data")
    else:

        with st.form("form"):
            data = {}
            c1, c2 = st.columns(2)

            for i, f in enumerate(columns):
                target = c1 if i % 2 == 0 else c2

                with target:
                    if f == "Date":
                        data[f] = st.text_input(f, value=str(datetime.now().date()))
                    else:
                        data[f] = st.text_input(f)

            if st.form_submit_button("Save"):
                if data["Battery Cassette ID"] == "":
                    st.error("ID required")
                else:
                    save_record(data)
                    st.success("Saved")

# ==========================
# TAB 2 - DATABASE
# ==========================

with tab2:

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if st.session_state.role == "admin" and not df.empty:
        cid = st.selectbox("Delete ID", df["Battery Cassette ID"].astype(str))

        if st.button("Delete Record"):
            delete_record(cid)
            st.success("Deleted")
            st.rerun()

# ==========================
# TAB 3 - ANALYTICS
# ==========================

with tab3:

    df = load_data()

    if not df.empty:
        col = st.selectbox("Column", df.columns)
        st.bar_chart(df[col].value_counts())
    else:
        st.warning("No data")

# ==========================
# TAB 4 - USER MANAGEMENT
# ==========================

with tab4:

    st.subheader("👥 User Management")

    if st.session_state.role != "admin":
        st.warning("Only admin allowed")
    else:

        # CREATE USER
        st.markdown("### ➕ Create User")

        with st.form("create"):
            un = st.text_input("Username")
            pw = st.text_input("Password")
            rl = st.selectbox("Role", ["admin", "user"])

            if st.form_submit_button("Create"):
                add_user(un, pw, rl)
                st.success("User created")
                st.rerun()

        # VIEW USERS
        st.markdown("### 📋 Users")
        users = get_users()
        st.dataframe(users, use_container_width=True)

        # EDIT USER
        st.markdown("### ✏️ Edit User")

        selected = st.selectbox("Select User", users["username"].tolist())

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (selected,))
        udata = cur.fetchone()
        conn.close()

        if udata:
            with st.form("edit"):
                new_u = st.text_input("Username", value=udata[0])
                new_p = st.text_input("Password", value=udata[1])
                new_r = st.selectbox("Role", ["admin", "user"], index=0 if udata[2]=="admin" else 1)

                if st.form_submit_button("Update"):
                    update_user(selected, new_u, new_p, new_r)
                    st.success("Updated")
                    st.rerun()

        # DELETE USER
        st.markdown("### 🗑 Delete User")

        del_list = users["username"].tolist()
        if "admin" in del_list:
            del_list.remove("admin")

        if del_list:
            du = st.selectbox("Delete User", del_list)

            if st.button("Delete User"):
                delete_user(du)
                st.success("Deleted")
                st.rerun()
