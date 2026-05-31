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
# DB
# ==========================

def get_conn():
    return sqlite3.connect(DB)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        login_time TEXT
    )
    """)

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


def signup_user(username, password):
    conn = get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO users(username, password, role, active)
        VALUES (?, ?, 'User', 1)
        """, (username, password))

        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# ==========================
# DATA
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


def delete_record(cid):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM cassette WHERE "Battery Cassette ID"=?
    """, (cid,))

    conn.commit()
    conn.close()


# ==========================
# UPDATE (ADMIN EDIT)
# ==========================

def update_record(cassette_id, data):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE cassette SET
        Date=?,
        "BMS Software Version"=?,
        Voltage=?,
        Current=?,
        Temperature=?,
        "SOC %"=?,
        "SOH %"=?,
        "Cycle Count"=?,
        "Distance Covered Km"=?,
        "Issue-Free Km"=?,
        "Root Cause"=?,
        "Issue Status"=?,
        "Overall Status"=?,
        "Fault Code"=?,
        "Battery Health"=?,
        "Over Heating"=?,
        "Cell Imbalance"=?,
        "Connector Issue"=?,
        "Charging Issue"=?,
        "Discharging Issue"=?,
        Remarks=?,
        "Application Area"=?,
        "Current Location"=?
    WHERE "Battery Cassette ID"=?
    """, (
        data["Date"],
        data["BMS Software Version"],
        data["Voltage"],
        data["Current"],
        data["Temperature"],
        data["SOC %"],
        data["SOH %"],
        data["Cycle Count"],
        data["Distance Covered Km"],
        data["Issue-Free Km"],
        data["Root Cause"],
        data["Issue Status"],
        data["Overall Status"],
        data["Fault Code"],
        data["Battery Health"],
        data["Over Heating"],
        data["Cell Imbalance"],
        data["Connector Issue"],
        data["Charging Issue"],
        data["Discharging Issue"],
        data["Remarks"],
        data["Application Area"],
        data["Current Location"],
        cassette_id
    ))

    conn.commit()
    conn.close()


# ==========================
# SESSION
# ==========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==========================
# LOGIN / SIGNUP PAGE
# ==========================

if not st.session_state.logged_in:

    st.title("🔐 Cassette Operation System")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):

            user = login_user(u, p)

            if user:

                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.role = user[1]

                conn = get_conn()
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO login_history(username, login_time)
                VALUES (?,?)
                """, (u, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()

                st.rerun()

            else:
                st.error("Invalid login")

    with tab2:

        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")

        if st.button("Signup"):

            if signup_user(nu, np):
                st.success("Account Created")
            else:
                st.error("Username exists")

    st.stop()

# ==========================
# MAIN APP
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
# ADD
# ==========================

with tab1:

    with st.form("form"):

        data = {}
        c1, c2 = st.columns(2)

        for i, f in enumerate(columns):

            target = c1 if i % 2 == 0 else c2

            with target:

                if f == "Date":
                    data[f] = st.text_input(f, value=datetime.now().strftime("%d-%m-%Y"))

                elif f == "Issue Status":
                    data[f] = st.selectbox(f, ["GREEN","YELLOW","RED","WHITE"])

                elif f == "Battery Health":
                    data[f] = st.selectbox(f, ["GOOD","AVERAGE","CRITICAL"])

                else:
                    data[f] = st.text_input(f)

        if st.form_submit_button("Save"):
            if data["Battery Cassette ID"] == "":
                st.error("ID required")
            else:
                save_record(data)
                st.success("Saved")

# ==========================
# DATABASE
# ==========================

with tab2:

    df = load_data()

    search = st.text_input("Search")

    if search:
        df = df[df.astype(str).apply(lambda r: r.str.contains(search, case=False).any(), axis=1)]

    st.dataframe(df, use_container_width=True)

    st.download_button("Download CSV", df.to_csv(index=False), "data.csv", "text/csv")

    # DELETE
    if st.session_state.role == "Admin" and len(df) > 0:

        cid = st.selectbox("Select ID", df["Battery Cassette ID"].astype(str).unique())

        if st.button("Delete"):
            delete_record(cid)
            st.rerun()

    # EDIT (ADMIN)
    if st.session_state.role == "Admin" and len(df) > 0:

        st.subheader("✏️ Edit Record")

        cid = st.selectbox("Select Cassette to Edit", df["Battery Cassette ID"].astype(str).unique(), key="edit")

        row = df[df["Battery Cassette ID"] == cid].iloc[0]

        with st.form("edit_form"):

            new_data = {}

            c1, c2 = st.columns(2)

            for i, f in enumerate(columns):

                target = c1 if i % 2 == 0 else c2

                with target:

                    val = row[f]

                    if f == "Issue Status":
                        new_data[f] = st.selectbox(f, ["GREEN","YELLOW","RED","WHITE"], index=["GREEN","YELLOW","RED","WHITE"].index(val))

                    elif f == "Battery Health":
                        new_data[f] = st.selectbox(f, ["GOOD","AVERAGE","CRITICAL"], index=["GOOD","AVERAGE","CRITICAL"].index(val))

                    else:
                        new_data[f] = st.text_input(f, value=str(val))

            if st.form_submit_button("Update"):
                update_record(cid, new_data)
                st.success("Updated")
                st.rerun()

# ==========================
# ANALYTICS
# ==========================

with tab3:

    df = load_data()

    if df.empty:
        st.warning("No Data")
    else:

        col = st.selectbox("Parameter", df.columns)

        counts = df[col].astype(str).value_counts()

        fig, ax = plt.subplots()
        ax.bar(counts.index, counts.values)

        st.pyplot(fig)

        st.write("Total Records:", len(df))
