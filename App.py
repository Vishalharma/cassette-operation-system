
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

st.set_page_config(page_title="Cassette Operation System", layout="wide")
DB="cassette.db"

def conn():
    return sqlite3.connect(DB, check_same_thread=False)

def hpw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    c=conn(); cur=c.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    status TEXT)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS login_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    login_time TEXT,
    status TEXT)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS cassette(
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
    remarks TEXT)""")

    cur.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users VALUES(?,?,?,?)",
            ("admin", hpw("admin123"), "Admin", "Active")
        )

    c.commit(); c.close()

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if not st.session_state.logged_in:
    st.title("Login")

    u=st.text_input("Username")
    p=st.text_input("Password", type="password")

    if st.button("Login"):
        c=conn()
        q=pd.read_sql_query(
            "SELECT * FROM users WHERE username=? AND password=? AND status='Active'",
            c,
            params=(u,hpw(p))
        )

        c.execute(
            "INSERT INTO login_history(username,login_time,status) VALUES(?,?,?)",
            (u,str(datetime.now()),"Success" if len(q) else "Failed")
        )
        c.commit(); c.close()

        if len(q):
            st.session_state.logged_in=True
            st.session_state.role=q.iloc[0]["role"]
            st.rerun()
        else:
            st.error("Invalid Login")
    st.stop()

st.title("🔋 Cassette Operation System")

if st.button("Logout"):
    st.session_state.logged_in=False
    st.rerun()

t1,t2,t3,t4,t5=st.tabs(
["Add Record","Database","Edit","Analytics","Users"]
)

with t1:
    with st.form("add"):
        cid=st.text_input("Cassette ID")
        bms=st.text_input("BMS Version")
        voltage=st.text_input("Voltage")
        current=st.text_input("Current")
        temp=st.text_input("Temperature")
        soc=st.text_input("SOC")
        soh=st.text_input("SOH")
        cycle=st.text_input("Cycle Count")
        fault=st.text_input("Fault Code")
        loc=st.text_input("Location")
        remarks=st.text_input("Remarks")

        if st.form_submit_button("Save"):
            c=conn()
            c.execute("""INSERT OR REPLACE INTO cassette
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (str(datetime.now().date()),cid,bms,voltage,current,temp,soc,soh,cycle,fault,loc,remarks))
            c.commit(); c.close()
            st.success("Saved")

with t2:
    c=conn()
    df=pd.read_sql_query("SELECT * FROM cassette",c)
    c.close()

    search=st.text_input("Search Cassette ID")

    if search:
        df=df[df["cassette_id"].astype(str).str.contains(search,case=False,na=False)]

    st.dataframe(df,use_container_width=True)

    st.download_button(
        "Export CSV",
        df.to_csv(index=False).encode(),
        "cassette.csv",
        "text/csv"
    )

    if not df.empty:
        sel=st.selectbox("Select Cassette",df["cassette_id"])
        row=df[df["cassette_id"]==sel].iloc[0]
        st.write(row)

        if st.button("Delete Cassette"):
            c=conn()
            c.execute("DELETE FROM cassette WHERE cassette_id=?",(sel,))
            c.commit(); c.close()
            st.rerun()

with t3:
    c=conn()
    df=pd.read_sql_query("SELECT * FROM cassette",c)
    c.close()

    if not df.empty:
        sel=st.selectbox("Edit Cassette",df["cassette_id"])
        row=df[df["cassette_id"]==sel].iloc[0]

        voltage=st.text_input("New Voltage",row["voltage"])
        current=st.text_input("New Current",row["current"])

        if st.button("Update Record"):
            c=conn()
            c.execute(
                "UPDATE cassette SET voltage=?, current=? WHERE cassette_id=?",
                (voltage,current,sel)
            )
            c.commit(); c.close()
            st.success("Updated")

with t4:
    c=conn()
    df=pd.read_sql_query("SELECT * FROM cassette",c)
    c.close()

    st.metric("Total Records",len(df))

    if not df.empty:
        st.bar_chart(df["fault_code"].astype(str).value_counts())

with t5:
    if st.session_state.role=="Admin":
        uname=st.text_input("Username")
        upass=st.text_input("Password")
        role=st.selectbox("Role",["Admin","Engineer","Operator","Viewer"])
        status=st.selectbox("Status",["Active","Inactive"])

        if st.button("Save User"):
            c=conn()
            c.execute(
                "INSERT OR REPLACE INTO users VALUES(?,?,?,?)",
                (uname,hpw(upass),role,status)
            )
            c.commit(); c.close()
            st.success("User Saved")

        c=conn()
        users=pd.read_sql_query("SELECT username,role,status FROM users",c)
        logs=pd.read_sql_query("SELECT * FROM login_history ORDER BY id DESC",c)
        c.close()

        st.subheader("Users")
        st.dataframe(users,use_container_width=True)

        st.subheader("Login History")
        st.dataframe(logs,use_container_width=True)
    else:
        st.warning("Admin only")
