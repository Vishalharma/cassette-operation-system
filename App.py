import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

st.set_page_config(page_title="Cassette Operation System", layout="wide")

DATA_FILE = "cassette_data.csv"
USER_FILE = "users.csv"
LOG_FILE = "login_history.csv"

# ---------------- INIT FILES ----------------

def init_file(file, columns):
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

init_file(DATA_FILE, [
    "Date","cassette_id","bms_version","voltage","current",
    "temperature","soc","soh","cycle_count","fault_code",
    "location","remarks"
])

init_file(USER_FILE, ["username","password","role","status"])
init_file(LOG_FILE, ["username","time","status"])

# Default admin
users = pd.read_csv(USER_FILE)
if not ((users["username"] == "admin").any()):
    admin = pd.DataFrame([{
        "username": "admin",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "Admin",
        "status": "Active"
    }])
    users = pd.concat([users, admin], ignore_index=True)
    users.to_csv(USER_FILE, index=False)

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = ""

# ---------------- LOGIN ----------------

if not st.session_state.logged_in:

    st.title("🔐 Login - Cassette System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        users = pd.read_csv(USER_FILE)

        hashed = hashlib.sha256(password.encode()).hexdigest()

        user = users[
            (users["username"] == username) &
            (users["password"] == hashed) &
            (users["status"] == "Active")
        ]

        status = "Success" if not user.empty else "Failed"

        logs = pd.read_csv(LOG_FILE)
        logs = pd.concat([logs, pd.DataFrame([{
            "username": username,
            "time": str(datetime.now()),
            "status": status
        }])], ignore_index=True)
        logs.to_csv(LOG_FILE, index=False)

        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.role = user.iloc[0]["role"]
            st.rerun()
        else:
            st.error("Invalid Login")

    st.stop()

# ---------------- MAIN UI ----------------

st.title("🔋 Cassette Operation System")

col1, col2 = st.columns([8,2])

with col2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = ""
        st.rerun()

tabs = st.tabs(["Add","Database","Edit","Analytics","Users"])

# ---------------- ADD ----------------

with tabs[0]:

    with st.form("add"):

        cid = st.text_input("Cassette ID")
        bms = st.text_input("BMS Version")
        voltage = st.text_input("Voltage")
        current = st.text_input("Current")
        temp = st.text_input("Temperature")
        soc = st.text_input("SOC")
        soh = st.text_input("SOH")
        cycle = st.text_input("Cycle Count")
        fault = st.text_input("Fault Code")
        loc = st.text_input("Location")
        remarks = st.text_input("Remarks")

        if st.form_submit_button("Save"):

            df = pd.read_csv(DATA_FILE)

            df = pd.concat([df, pd.DataFrame([{
                "Date": str(datetime.now().date()),
                "cassette_id": cid,
                "bms_version": bms,
                "voltage": voltage,
                "current": current,
                "temperature": temp,
                "soc": soc,
                "soh": soh,
                "cycle_count": cycle,
                "fault_code": fault,
                "location": loc,
                "remarks": remarks
            }])], ignore_index=True)

            df.to_csv(DATA_FILE, index=False)
            st.success("Saved")

# ---------------- DATABASE ----------------

with tabs[1]:

    df = pd.read_csv(DATA_FILE)

    search = st.text_input("Search Cassette")

    if search:
        df = df[df["cassette_id"].astype(str).str.contains(search, na=False)]

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Export CSV",
        df.to_csv(index=False).encode(),
        "cassette.csv",
        "text/csv"
    )

    if not df.empty:
        sel = st.selectbox("Select", df["cassette_id"])
        st.write(df[df["cassette_id"] == sel])

        if st.button("Delete"):
            df = df[df["cassette_id"] != sel]
            df.to_csv(DATA_FILE, index=False)
            st.success("Deleted")
            st.rerun()

# ---------------- EDIT ----------------

with tabs[2]:

    df = pd.read_csv(DATA_FILE)

    if not df.empty:

        sel = st.selectbox("Edit Cassette", df["cassette_id"])
        row = df[df["cassette_id"] == sel].iloc[0]

        voltage = st.text_input("Voltage", row["voltage"])
        current = st.text_input("Current", row["current"])

        if st.button("Update"):

            idx = df[df["cassette_id"] == sel].index[0]

            df.loc[idx, "voltage"] = voltage
            df.loc[idx, "current"] = current

            df.to_csv(DATA_FILE, index=False)
            st.success("Updated")

# ---------------- ANALYTICS ----------------

with tabs[3]:

    df = pd.read_csv(DATA_FILE)

    st.metric("Total Records", len(df))

    if not df.empty:

        st.subheader("Fault Code Distribution")

        st.bar_chart(df["fault_code"].astype(str).value_counts())

# ---------------- USERS ----------------

with tabs[4]:

    if st.session_state.role == "Admin":

        st.subheader("User Management")

        uname = st.text_input("Username")
        upass = st.text_input("Password", type="password")

        role = st.selectbox("Role", ["Admin","Engineer","Operator","Viewer"])
        status = st.selectbox("Status", ["Active","Inactive"])

        if st.button("Add User"):

            users = pd.read_csv(USER_FILE)

            users = pd.concat([users, pd.DataFrame([{
                "username": uname,
                "password": hashlib.sha256(upass.encode()).hexdigest(),
                "role": role,
                "status": status
            }])], ignore_index=True)

            users.to_csv(USER_FILE, index=False)
            st.success("User Added")

        st.subheader("Users")
        st.dataframe(pd.read_csv(USER_FILE), use_container_width=True)

        st.subheader("Login History")
        st.dataframe(pd.read_csv(LOG_FILE), use_container_width=True)

    else:
        st.warning("Admin only")
