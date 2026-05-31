# Users Table
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    status TEXT
)
""")

# Login History
cur.execute("""
CREATE TABLE IF NOT EXISTS login_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    login_time TEXT,
    status TEXT
)
""")

# Default Admin
cur.execute("""
INSERT OR IGNORE INTO users
VALUES('admin','admin123','Admin','Active')
""")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        conn = get_conn()

        q = pd.read_sql_query(
            """
            SELECT * FROM users
            WHERE username=?
            AND password=?
            AND status='Active'
            """,
            conn,
            params=(user, pwd)
        )

        if len(q):

            st.session_state.logged_in = True
            st.session_state.username = user
            st.session_state.role = q.iloc[0]["role"]

            conn.execute(
                "INSERT INTO login_history(username,login_time,status) VALUES(?,?,?)",
                (user, str(datetime.now()), "Success")
            )
            conn.commit()

            st.rerun()

        else:
            st.error("Invalid Login")

        conn.close()

    st.stop()
    col1, col2 = st.columns([8,1])

with col2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
        search = st.text_input("🔍 Search Cassette ID")

if search:
    df = df[
        df["Battery Cassette ID"]
        .astype(str)
        .str.contains(search, case=False, na=False)
    ]
    selected_id = st.selectbox(
    "Select Cassette",
    [""] + df["Battery Cassette ID"].astype(str).tolist()
)

if selected_id:

    row = df[df["Battery Cassette ID"] == selected_id].iloc[0]

    st.metric("Voltage", row["Voltage"])
    st.metric("SOC", row["SOC %"])
    st.metric("SOH", row["SOH %"])

    st.write("Root Cause:", row["Root Cause"])
    st.write("Location:", row["Current Location"])
    csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Export CSV",
    csv,
    "cassette_records.csv",
    "text/csv"
)
tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add Entry",
    "📊 Database",
    "📈 Analytics",
    "✏ Edit Record"
])
with tab4:

    df = load_data()

    if not df.empty:

        cid = st.selectbox(
            "Select Cassette",
            df["Battery Cassette ID"].tolist()
        )

        row = df[df["Battery Cassette ID"] == cid].iloc[0]

        voltage = st.text_input(
            "Voltage",
            value=row["Voltage"]
        )

        current = st.text_input(
            "Current",
            value=row["Current"]
        )

        if st.button("Update"):

            conn = get_conn()

            conn.execute("""
            UPDATE cassette
            SET Voltage=?,
                Current=?
            WHERE "Battery Cassette ID"=?
            """,
            (voltage, current, cid))

            conn.commit()
            conn.close()

            st.success("Updated")
            if st.session_state.role == "Admin":

    st.subheader("👤 User Management")

    uname = st.text_input("Username")
    pwd = st.text_input("Password")
    role = st.selectbox(
        "Role",
        ["Admin","Engineer","Operator","Viewer"]
    )

    status = st.selectbox(
        "Status",
        ["Active","Inactive"]
    )

    if st.button("Create User"):

        conn = get_conn()

        conn.execute("""
        INSERT OR REPLACE INTO users
        VALUES(?,?,?,?)
        """,
        (uname,pwd,role,status))

        conn.commit()
        conn.close()

        st.success("User Created")
        
