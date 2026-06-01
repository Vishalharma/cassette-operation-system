import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="OEM EOL Checklist System", layout="wide")

FILE = "eol_checklist.csv"

SECTIONS = ["Mechanical", "Battery_BMS", "Electrical", "ICU", "TIU_Cloud"]

# ==========================
# PREDEFINED OEM CHECKLIST
# ==========================

PREDEFINED = {

"Mechanical": [
    "Physical appearance",
    "Dents/Bumps",
    "Dirt/Oil stains",
    "Cracks/Burrs",
    "Nameplate & Safety labels",
    "Dimensions (Height, Width, Length)",
    "Battery polarity marking",
    "Cassette Serial Number",
    "Clamps condition",
    "Wiring harness routing",
    "Thermal hoses",
    "Torque verification",
    "Overall weight",
    "Cassette dimensions",
    "Cooling flow",
    "Coolant temperature",
    "Coolant leakage (Static)",
    "Coolant leakage (Dynamic)",
    "Swap connector visual inspection",
    "Pin mating verification",
    "Power connector inspection"
],

"Battery_BMS": [
    "Pack Serial Number",
    "Shipping SOC",
    "Battery SOC @50%",
    "Vmax",
    "Vmin",
    "Tmax",
    "Tmin",
    "Delta V",
    "Pack Voltage",
    "Delta T",
    "BMS Software Version",
    "BMS Hardware Version",
    "Insulation Resistance",
    "AIS038 Insulation Test",
    "Hall Effect Sensor",
    "Pressure Sensor",
    "Humidity Sensor",
    "Leakage Sensor",
    "Smoke Sensor",
    "Full Charge Cycle Test",
    "Full Discharge Cycle Test",
    "Temperature Rise",
    "Dispense Time"
],

"Electrical": [
    "24V Supply",
    "CAN Communication",
    "HVB Detection",
    "Main Positive Relay",
    "Main Negative Relay",
    "Precharge Relay",
    "Cell Voltage Reading",
    "Continuity Test",
    "Connection Robustness",
    "DC-DC Function",
    "MSD Verification",
    "IGN Signal",
    "Charge Enable",
    "TMS ON",
    "HVIL Loop Check",
    "Power ON Test",
    "Contactor ON Test"
],

"ICU": [
    "ICU Hardware Version",
    "ICU Software Version",
    "Verification Software Version",
    "Data Matching ICU vs BMS",
    "HVIL Reading",
    "Inlet Temperature",
    "Outlet Temperature",
    "Leakage Sensor Reading",
    "Ambient Temperature",
    "Charge Enable Signal",
    "Requested Current",
    "CC/CV Verification"
],

"TIU_Cloud": [
    "TIU Hardware Version",
    "TIU Software Version",
    "Cloud Data Sync",
    "TIU Communication Check",
    "Final Data Matching",
    "Cloud Upload Verification"
]
}

# ==========================
# INIT FILE
# ==========================

if not os.path.exists(FILE):
    pd.DataFrame(columns=[
        "Cassette_ID","Section","Parameter","Actual","Result","Inspector","Notes"
    ]).to_csv(FILE, index=False)

# ==========================
# UI
# ==========================

st.title("🔋 OEM EOL Checklist System (Sun Mobility Style)")

tab1, tab2 = st.tabs(["🧾 Checklist Entry", "📊 Dashboard + Excel"])

# ==========================
# TAB 1 - ENTRY
# ==========================

with tab1:

    st.subheader("Enter EOL Data")

    cassette_id = st.text_input("Cassette ID")
    section = st.selectbox("Section", SECTIONS)

    st.markdown("### 📋 Predefined Checklist")

    checklist = PREDEFINED[section]

    entries = []

    with st.form("form"):

        inspector = st.text_input("Inspector")

        for item in checklist:

            st.markdown(f"**{item}**")

            col1, col2 = st.columns(2)

            with col1:
                actual = st.text_input(f"Actual - {item}")

            with col2:
                result = st.selectbox(
                    f"Result - {item}",
                    ["Pass", "Fail", "Pending"],
                    key=item
                )

            notes = st.text_input(f"Notes - {item}")

            entries.append({
                "Cassette_ID": cassette_id,
                "Section": section,
                "Parameter": item,
                "Actual": actual,
                "Result": result,
                "Inspector": inspector,
                "Notes": notes
            })

        submit = st.form_submit_button("Save Full Section")

        if submit:

            df_new = pd.DataFrame(entries)
            df_old = pd.read_csv(FILE)

            pd.concat([df_old, df_new], ignore_index=True).to_csv(FILE, index=False)

            st.success("Section Saved Successfully 🚀")
            st.rerun()

# ==========================
# TAB 2 - DASHBOARD
# ==========================

with tab2:

    st.subheader("📊 EOL Dashboard")

    df = pd.read_csv(FILE)

    if df.empty:
        st.warning("No data")
        st.stop()

    # FILTERS
    c1, c2 = st.columns(2)

    with c1:
        sec = st.selectbox("Filter Section", ["All"] + SECTIONS)

    with c2:
        cassette = st.selectbox("Filter Cassette", ["All"] + list(df["Cassette_ID"].unique()))

    if sec != "All":
        df = df[df["Section"] == sec]

    if cassette != "All":
        df = df[df["Cassette_ID"] == cassette]

    # SEARCH
    search = st.text_input("🔍 Search")

    if search:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]

    # SUMMARY
    c1, c2, c3 = st.columns(3)

    c1.metric("Total", len(df))
    c2.metric("Pass", (df["Result"] == "Pass").sum())
    c3.metric("Fail", (df["Result"] == "Fail").sum())

    # FAIL TABLE
    st.markdown("### ❌ Failed Items")
    st.dataframe(df[df["Result"] == "Fail"], use_container_width=True)

    # FULL TABLE
    st.markdown("### 📋 Full Data")

    def color(row):
        if row["Result"] == "Fail":
            return ["background-color:#ffcccc"] * len(row)
        return [""] * len(row)

    st.dataframe(df.style.apply(color, axis=1), use_container_width=True)

    # ==========================
    # EXPORT EXCEL (SHEET WISE)
    # ==========================

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        for sec in SECTIONS:
            df[df["Section"] == sec].to_excel(writer, sheet_name=sec, index=False)

        summary = df["Result"].value_counts().reset_index()
        summary.columns = ["Result", "Count"]
        summary.to_excel(writer, sheet_name="Summary", index=False)

    st.download_button(
        "📥 Download OEM EOL Excel (Section Wise)",
        output.getvalue(),
        file_name="OEM_EOL_Checklist.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
