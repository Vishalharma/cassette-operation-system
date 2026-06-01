import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import matplotlib.pyplot as plt
import io

# ==========================
# CONFIG
# ==========================

st.set_page_config(page_title="Cassette Operation System", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "cassette.db")
EOL_FILE = os.path.join(BASE_DIR, "eol_report.csv")

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

    conn.commit()
    conn.close()

init_db()

# ==========================
# COLUMNS
# ==========================

columns = [
    "Date","Battery Cassette ID","BMS Software Version","Voltage","Current",
    "Temperature","SOC %","SOH %","Cycle Count","Distance Covered Km",
    "Issue-Free Km","Root Cause","Issue Status","Overall Status","Fault Code",
    "Battery Health","Over Heating","Cell Imbalance","Connector Issue",
    "Charging Issue","Discharging Issue","Remarks","Application Area",
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
    cur = conn.cursor()

    cols = ", ".join([f'"{c}"' for c in columns])
    placeholders = ", ".join(["?"] * len(columns))
    values = tuple(data.get(c, "") for c in columns)

    cur.execute(f"""
    INSERT OR REPLACE INTO cassette ({cols})
    VALUES ({placeholders})
    """, values)

    conn.commit()
    conn.close()


def delete_record(cid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM cassette WHERE "Battery Cassette ID"=?', (cid,))
    conn.commit()
    conn.close()

# ==========================
# UI
# ==========================

st.title("🔋 Cassette Operation System")

tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add Entry",
    "📊 Database",
    "📈 Analytics",
    "📋 EOL Test System"
])

# ==========================
# TAB 1 - ADD ENTRY
# ==========================

with tab1:

    st.subheader("Add New Record")

    with st.form("add_form"):
        data = {}
        c1, c2 = st.columns(2)

        for i, f in enumerate(columns):
            target = c1 if i % 2 == 0 else c2
            with target:
                if f == "Date":
                    data[f] = st.text_input(f, value=str(datetime.now().date()))
                else:
                    data[f] = st.text_input(f)

        submit = st.form_submit_button("Save")

        if submit:
            if data["Battery Cassette ID"].strip() == "":
                st.error("Battery Cassette ID required")
            else:
                save_record(data)
                st.success("Record saved successfully")
                st.rerun()

# ==========================
# TAB 2 - DATABASE
# ==========================

with tab2:

    st.subheader("All Records")

    df = load_data()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        cid = st.selectbox("Delete Cassette ID", df["Battery Cassette ID"].astype(str))

        if st.button("Delete"):
            delete_record(cid)
            st.success("Deleted successfully")
            st.rerun()

# ==========================
# TAB 3 - ANALYTICS
# ==========================

with tab3:

    st.subheader("Analytics Dashboard")

    df = load_data()

    if df.empty:
        st.warning("No data available")
    else:
        col = st.selectbox("Select Parameter", df.columns)

        counts = df[col].astype(str).value_counts()

        fig, ax = plt.subplots()
        ax.bar(counts.index, counts.values)
        plt.xticks(rotation=45)

        st.pyplot(fig)

        st.metric("Total Records", len(df))

# ==========================
# TAB 4 - EOL SYSTEM (FULL STRUCTURED)
# ==========================

with tab4:

    st.subheader("📋 EOL Test System (Mechanical / Electrical / Battery / ICU / TIU)")

    # ==========================
    # INIT FILE
    # ==========================
    if not os.path.exists(EOL_FILE):
        pd.DataFrame(columns=[
            "Battery Cassette ID","Category","Step","Area","Test Item",
            "Requirement","Expected","Actual","Result","Inspector","Notes"
        ]).to_csv(EOL_FILE, index=False)

    # ==========================
    # INPUT FORM
    # ==========================
    with st.form("eol_form"):

        st.markdown("### 🧩 Add EOL Test Data")

        cassette_id = st.text_input("Battery Cassette ID")

        category = st.selectbox(
            "Category",
            ["Mechanical", "Electrical", "Battery", "ICU", "TIU"]
        )

        c1, c2 = st.columns(2)

        with c1:
            step = st.text_input("Step")
            area = st.text_input("Area")
            test_item = st.text_input("Test Item")
            requirement = st.text_input("Requirement")

        with c2:
            expected = st.text_input("Expected")
            actual = st.text_input("Actual")
            inspector = st.text_input("Inspector")
            notes = st.text_input("Notes")

        result = st.selectbox("Result", ["Pass", "Fail", "NA"])

        submit = st.form_submit_button("Save EOL")

        if submit:

            new_row = pd.DataFrame([{
                "Battery Cassette ID": cassette_id,
                "Category": category,
                "Step": step,
                "Area": area,
                "Test Item": test_item,
                "Requirement": requirement,
                "Expected": expected,
                "Actual": actual,
                "Result": result,
                "Inspector": inspector,
                "Notes": notes
            }])

            old = pd.read_csv(EOL_FILE)
            updated = pd.concat([old, new_row], ignore_index=True)
            updated.to_csv(EOL_FILE, index=False)

            st.success("EOL Record Saved 🚀")
            st.rerun()

    # ==========================
    # VIEW + FILTER + DASHBOARD
    # ==========================
    st.markdown("---")
    st.subheader("📊 EOL Records")

    df = pd.read_csv(EOL_FILE)

    if not df.empty:

        c1, c2 = st.columns(2)

        with c1:
            cat_filter = st.selectbox("Category Filter", ["All"] + list(df["Category"].unique()))

        with c2:
            cassette_filter = st.selectbox("Cassette Filter", ["All"] + list(df["Battery Cassette ID"].unique()))

        if cat_filter != "All":
            df = df[df["Category"] == cat_filter]

        if cassette_filter != "All":
            df = df[df["Battery Cassette ID"] == cassette_filter]

        # SEARCH
        search = st.text_input("🔍 Search EOL Data")

        if search:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]

        # ==========================
        # DASHBOARD
        # ==========================
        if "Result" in df.columns:

            pass_count = (df["Result"] == "Pass").sum()
            fail_count = (df["Result"] == "Fail").sum()

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Steps", len(df))
            c2.metric("Pass", pass_count)
            c3.metric("Fail", fail_count)

            fig, ax = plt.subplots()
            df["Result"].value_counts().plot(kind="bar", ax=ax)
            st.pyplot(fig)

        # ==========================
        # FAIL HIGHLIGHT
        # ==========================
        def highlight(row):
            if row["Result"] == "Fail":
                return ["background-color: #ffcccc"] * len(row)
            return [""] * len(row)

        st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True)

        # ==========================
        # EXPORT EXCEL
        # ==========================
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="EOL")

        st.download_button(
            "📥 Download EOL Excel",
            output.getvalue(),
            file_name="EOL_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info("No EOL data found")
