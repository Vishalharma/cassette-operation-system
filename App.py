import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="OEM EOL System", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE_DIR, "eol_data.csv")

SECTIONS = [
    "Mechanical",
    "Battery_BMS",
    "Electrical",
    "ICU",
    "TIU_Cloud",
    "Quality"
]

# ==========================
# INIT FILE
# ==========================
if not os.path.exists(FILE):
    pd.DataFrame(columns=[
        "Cassette_ID","Section","Parameter","Sub_Parameter",
        "Expected","Actual","Result","Inspector","Notes"
    ]).to_csv(FILE, index=False)

# ==========================
# UI
# ==========================

st.title("🔋 Sun Mobility OEM EOL System")

tab1, tab2 = st.tabs(["🧾 EOL Entry", "📊 Dashboard & Excel Export"])

# ==========================
# TAB 1 - ENTRY
# ==========================

with tab1:

    st.subheader("Enter EOL Data (Structured)")

    with st.form("form"):

        cassette_id = st.text_input("Cassette ID")
        section = st.selectbox("Section", SECTIONS)

        st.markdown("### 📋 Parameters Input")

        parameter = st.text_input("Main Parameter (e.g. Mechanical Inspection)")
        sub_parameter = st.text_input("Sub Parameter")

        col1, col2 = st.columns(2)

        with col1:
            expected = st.text_input("Expected Value")
            actual = st.text_input("Actual Value")

        with col2:
            inspector = st.text_input("Inspector")
            notes = st.text_input("Notes")

        result = st.selectbox("Result", ["Pass", "Fail", "Pending"])

        submit = st.form_submit_button("Save")

        if submit:

            new = pd.DataFrame([{
                "Cassette_ID": cassette_id,
                "Section": section,
                "Parameter": parameter,
                "Sub_Parameter": sub_parameter,
                "Expected": expected,
                "Actual": actual,
                "Result": result,
                "Inspector": inspector,
                "Notes": notes
            }])

            old = pd.read_csv(FILE)
            pd.concat([old, new], ignore_index=True).to_csv(FILE, index=False)

            st.success("Saved Successfully 🚀")
            st.rerun()

# ==========================
# TAB 2 - DASHBOARD
# ==========================

with tab2:

    st.subheader("📊 EOL Dashboard")

    df = pd.read_csv(FILE)

    if df.empty:
        st.warning("No data found")
        st.stop()

    # ==========================
    # FILTERS
    # ==========================

    c1, c2 = st.columns(2)

    with c1:
        sec_filter = st.selectbox("Filter Section", ["All"] + SECTIONS)

    with c2:
        cassette_filter = st.selectbox("Filter Cassette", ["All"] + list(df["Cassette_ID"].unique()))

    if sec_filter != "All":
        df = df[df["Section"] == sec_filter]

    if cassette_filter != "All":
        df = df[df["Cassette_ID"] == cassette_filter]

    # ==========================
    # SEARCH
    # ==========================

    search = st.text_input("🔍 Search")

    if search:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]

    # ==========================
    # SUMMARY
    # ==========================

    pass_count = (df["Result"] == "Pass").sum()
    fail_count = (df["Result"] == "Fail").sum()
    pending_count = (df["Result"] == "Pending").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(df))
    c2.metric("Pass", pass_count)
    c3.metric("Fail", fail_count)
    c4.metric("Pending", pending_count)

    # ==========================
    # FAIL TABLE
    # ==========================

    st.markdown("### ❌ Failed Items")

    st.dataframe(df[df["Result"] == "Fail"], use_container_width=True)

    st.markdown("### ⏳ Pending Items")

    st.dataframe(df[df["Result"] == "Pending"], use_container_width=True)

    # ==========================
    # FULL DATA
    # ==========================

    st.markdown("### 📋 Full EOL Data")

    def color(row):
        if row["Result"] == "Fail":
            return ["background-color:#ffcccc"] * len(row)
        elif row["Result"] == "Pending":
            return ["background-color:#fff3cd"] * len(row)
        return [""] * len(row)

    st.dataframe(df.style.apply(color, axis=1), use_container_width=True)

    # ==========================
    # EXPORT TO 5 SHEETS EXCEL
    # ==========================

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        for sec in SECTIONS:
            df[df["Section"] == sec].to_excel(writer, sheet_name=sec, index=False)

        # Summary Sheet
        summary = df["Result"].value_counts().reset_index()
        summary.columns = ["Result", "Count"]
        summary.to_excel(writer, sheet_name="Summary", index=False)

    st.download_button(
        "📥 Download OEM EOL Excel (5 Sheets)",
        output.getvalue(),
        file_name="OEM_EOL_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
