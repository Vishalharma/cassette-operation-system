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
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)

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

    # default admin
    cur.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users VALUES ('admin','admin123','admin')")

    conn.commit()
    conn.close()

init_db()

# ==========================
# AUTH
# ==========================

def authenticate(u, p):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT role FROM users WHERE username=? AND password=?", (u, p))
    r = cur.fetchone()

    conn.close()
    return r[0] if r else None

# ==========================
# USER FUNCTIONS
# ==========================

def get_users():
    conn = get_conn()
    df = pd.read_sql_query("SELECT username, role FROM users", conn)
    conn.close()
    return df


def update_user(old_u, new_u, new_p, new_r):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET username=?, password=?, role=?
    WHERE username=?
    """, (new_u, new_p, new_r, old_u))

    conn.commit()
    conn.close()


def add_user(u, p, r):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)", (u, p, r))

    conn.commit()
    conn.close()


def delete_user(u):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE username=?", (u,))

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
# BLOCK LOGIN
# ==========================

if not st.session_state.logged_in:
    login()
    st.stop()

# ==========================
# UI HEADER
# ==========================

st.title("🔋 Cassette Operation System")

st.sidebar.write("👤", st.session_state.username)
st.sidebar.write("🔐", st.session_state.role)

logout()

# ==========================
# TABS
# ==========================

tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add Entry",
    "📊 Database",
    "📈 Analytics",
    "👥 User Management"
])

# ==========================
# TAB 1
# ==========================

with tab1:

    st.subheader("Add Entry")

    if st.session_state.role != "admin":
        st.warning("Only admin can add data")
    else:
        st.info("Add cassette data here")

# ==========================
# TAB 2
# ==========================

with tab2:

    st.subheader("Database View")
    st.info("Your cassette data will show here")

# ==========================
# TAB 3
# ==========================

with tab3:

    st.subheader("Analytics")
    st.info("Charts here")

# ==========================
# TAB 4 - USER MANAGEMENT (FIXED)
# ==========================

with tab4:

    st.subheader("👥 User Management")

    if st.session_state.role != "admin":
        st.warning("Only admin allowed")
    else:

        # ================= CREATE USER =================
        st.markdown("### ➕ Create User")

        with st.form("create_user"):
            cu = st.text_input("Username")
            cp = st.text_input("Password")
            cr = st.selectbox("Role", ["admin", "user"])

            if st.form_submit_button("Create"):
                add_user(cu, cp, cr)
                st.success("User created")
                st.rerun()

        # ================= VIEW USERS =================
        st.markdown("### 📋 Users")
        users = get_users()
        st.dataframe(users, use_container_width=True)

        # ================= EDIT USER (FIXED SAFE) =================
        st.markdown("### ✏️ Edit User")

        if not users.empty:

            selected_user = st.selectbox(
                "Select User",
                users["username"].tolist(),
                key="edit_user"
            )

            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT username,password,role FROM users WHERE username=?", (selected_user,))
            udata = cur.fetchone()
            conn.close()

            if udata:

                with st.form("edit_form"):

                    nu = st.text_input("Username", value=udata[0])
                    np = st.text_input("Password", value=udata[1])
                    nr = st.selectbox(
                        "Role",
                        ["admin", "user"],
                        index=0 if udata[2] == "admin" else 1
                    )

                    if st.form_submit_button("Update"):
                        update_user(selected_user, nu, np, nr)
                        st.success("Updated successfully")
                        st.rerun()

        # ================= DELETE USER =================
        st.markdown("### 🗑 Delete User")

        del_list = users["username"].tolist()
        if "admin" in del_list:
            del_list.remove("admin")

        if del_list:
            du = st.selectbox("Select User", del_list, key="del_user")

            if st.button("Delete User"):
                delete_user(du)
                st.success("Deleted")
                st.rerun()

        # ================= PASSWORD CHANGE =================
        st.markdown("### 🔐 Change My Password")

        with st.form("pass_change"):
            cur_p = st.text_input("Current Password", type="password")
            new_p = st.text_input("New Password", type="password")

            if st.form_submit_button("Update Password"):

                conn = get_conn()
                cur = conn.cursor()

                cur.execute("SELECT password FROM users WHERE username=?", (st.session_state.username,))
                real = cur.fetchone()[0]

                if cur_p == real:
                    cur.execute("UPDATE users SET password=? WHERE username=?",
                                (new_p, st.session_state.username))
                    conn.commit()
                    st.success("Password updated")
                else:
                    st.error("Wrong current password")

                conn.close()
