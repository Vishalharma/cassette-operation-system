import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Cassette Operation System", layout="wide")

DATA_FILE = "cassette_data.csv"

# Create CSV if not exists
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "Date",
        "cassette_id",
        "bms_version",
        "voltage",
        "current",
        "temperature",
        "soc",
        "soh",
        "cycle_count",
        "fault_code",
        "location",
        "remarks"
    ]).to_csv(DATA_FILE, index=False)

st.title("🔋 Cassette Operation System")

tabs = st.tabs([
    "Add Record",
    "Database",
    "Edit",
    "Analytics"
])

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

        if st.form_submit_button("Save"):

            df = pd.read_csv(DATA_FILE)

            new_row = {
                "Date": str(datetime.now().date()),
                "cassette_id": cassette_id,
                "bms_version": bms_version,
                "voltage": voltage,
                "current": current,
                "temperature": temperature,
                "soc": soc,
                "soh": soh,
                "cycle_count": cycle_count,
                "fault_code": fault_code,
                "location": location,
                "remarks": remarks
            }

            df = pd.concat(
                [df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            df.to_csv(DATA_FILE, index=False)

            st.success("Record Saved")

# ---------------- DATABASE ----------------

with tabs[1]:

    df = pd.read_csv(DATA_FILE)

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
        "cassette_export.csv",
        "text/csv"
    )

# ---------------- EDIT ----------------

with tabs[2]:

    df = pd.read_csv(DATA_FILE)

    if not df.empty:

        selected = st.selectbox(
            "Select Cassette",
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

            idx = df[df["cassette_id"] == selected].index[0]

            df.loc[idx, "voltage"] = voltage
            df.loc[idx, "current"] = current

            df.to_csv(DATA_FILE, index=False)

            st.success("Updated")

# ---------------- ANALYTICS ----------------

with tabs[3]:

    df = pd.read_csv(DATA_FILE)

    st.metric("Total Records", len(df))

    if not df.empty:

        st.subheader("Fault Distribution")

        st.bar_chart(
            df["fault_code"]
            .astype(str)
            .value_counts()
        )
