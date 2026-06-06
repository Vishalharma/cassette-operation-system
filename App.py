import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Optional DBC support
try:
    import cantools
    DBC_AVAILABLE = True
except:
    DBC_AVAILABLE = False

st.set_page_config(
    page_title="CAN Studio Pro",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 CAN Studio Pro")
st.markdown("### EV / BMS CAN Analysis Platform")

menu = st.sidebar.selectbox(
    "Select Module",
    [
        "Home",
        "CAN Basics",
        "CAN Hardware",
        "DBC Explorer",
        "Log Analyzer",
        "Fault Simulator",
        "BMS Dashboard",
        "CAN Calculator",
        "Quiz"
    ]
)

# ---------------------------------------------------
# HOME
# ---------------------------------------------------

if menu == "Home":

    st.header("Welcome")

    st.write("""
    CAN Studio Pro Features:

    ✔ CAN Protocol Learning

    ✔ Hardware Reference

    ✔ DBC Explorer

    ✔ ASC / CSV Log Analysis

    ✔ Fault Simulator

    ✔ BMS Dashboard

    ✔ CAN Calculators

    ✔ Quiz Section
    """)

# ---------------------------------------------------
# CAN BASICS
# ---------------------------------------------------

elif menu == "CAN Basics":

    st.header("CAN Protocol Basics")

    st.subheader("What is CAN?")

    st.write("""
    Controller Area Network (CAN) is a robust communication
    protocol widely used in automotive and industrial systems.
    """)

    st.subheader("CAN Frame Structure")

    st.code("""
SOF
Identifier
RTR
IDE
DLC
DATA
CRC
ACK
EOF
""")

    st.subheader("CAN Types")

    st.table({
        "CAN Type": ["Standard", "Extended"],
        "Identifier": ["11 Bit", "29 Bit"]
    })

# ---------------------------------------------------
# CAN HARDWARE
# ---------------------------------------------------

elif menu == "CAN Hardware":

    st.header("CAN Hardware")

    st.subheader("Main Components")

    components = [
        "CAN Controller",
        "CAN Transceiver",
        "CANH",
        "CANL",
        "120Ω Termination"
    ]

    for c in components:
        st.success(c)

    st.subheader("Popular CAN Transceivers")

    df = pd.DataFrame({
        "Part Number": [
            "MCP2551",
            "TJA1042",
            "TCAN1042"
        ],
        "Type": [
            "Transceiver",
            "Transceiver",
            "Transceiver"
        ]
    })

    st.dataframe(df)

# ---------------------------------------------------
# DBC EXPLORER
# ---------------------------------------------------

elif menu == "DBC Explorer":

    st.header("DBC Explorer")

    if not DBC_AVAILABLE:

        st.error(
            "cantools not installed. "
            "Run: pip install cantools"
        )

    else:

        dbc_file = st.file_uploader(
            "Upload DBC File",
            type=["dbc"]
        )

        if dbc_file:

            try:

                db = cantools.database.load_string(
                    dbc_file.read().decode("utf-8")
                )

                st.success("DBC Loaded Successfully")

                for msg in db.messages:

                    with st.expander(msg.name):

                        st.write(
                            "Message ID:",
                            hex(msg.frame_id)
                        )

                        st.write(
                            "Length:",
                            msg.length
                        )

                        signals = []

                        for sig in msg.signals:

                            signals.append({
                                "Signal": sig.name,
                                "Start Bit": sig.start,
                                "Length": sig.length
                            })

                        st.dataframe(signals)

            except Exception as e:

                st.error(str(e))

# ---------------------------------------------------
# LOG ANALYZER
# ---------------------------------------------------

elif menu == "Log Analyzer":

    st.header("CSV Log Analyzer")

    file = st.file_uploader(
        "Upload CSV File",
        type=["csv"]
    )

    if file:

        df = pd.read_csv(file)

        st.subheader("Preview")

        st.dataframe(df.head())

        numeric_cols = list(
            df.select_dtypes(
                include=np.number
            ).columns
        )

        if len(numeric_cols) > 0:

            signal = st.selectbox(
                "Select Signal",
                numeric_cols
            )

            fig = px.line(
                df,
                y=signal,
                title=f"{signal} Trend"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.subheader("Statistics")

            st.write(
                df[signal].describe()
            )

# ---------------------------------------------------
# FAULT SIMULATOR
# ---------------------------------------------------

elif menu == "Fault Simulator":

    st.header("CAN Fault Simulator")

    fault = st.selectbox(
        "Select Fault",
        [
            "Bus Off",
            "Error Passive",
            "Missing Message",
            "CRC Error",
            "Bit Error",
            "Stuck Dominant",
            "Stuck Recessive"
        ]
    )

    fault_info = {

        "Bus Off":
        """
        Node disconnected due to
        excessive transmission errors.
        """,

        "Error Passive":
        """
        Communication still active
        but degraded.
        """,

        "Missing Message":
        """
        Timeout condition due to
        missing CAN frame.
        """,

        "CRC Error":
        """
        Frame corruption detected.
        """,

        "Bit Error":
        """
        Sent and received bit mismatch.
        """,

        "Stuck Dominant":
        """
        Bus held low continuously.
        """,

        "Stuck Recessive":
        """
        Bus remains idle continuously.
        """
    }

    st.warning(fault_info[fault])

# ---------------------------------------------------
# BMS DASHBOARD
# ---------------------------------------------------

elif menu == "BMS Dashboard":

    st.header("Battery Management Dashboard")

    col1, col2 = st.columns(2)

    with col1:

        soc = st.slider(
            "SOC %",
            0,
            100,
            80
        )

        voltage = st.number_input(
            "Pack Voltage",
            value=350.0
        )

    with col2:

        current = st.number_input(
            "Pack Current",
            value=50.0
        )

        temp = st.number_input(
            "Temperature",
            value=28.0
        )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "SOC",
        f"{soc}%"
    )

    m2.metric(
        "Voltage",
        f"{voltage:.1f} V"
    )

    m3.metric(
        "Current",
        f"{current:.1f} A"
    )

    m4.metric(
        "Temp",
        f"{temp:.1f} °C"
    )

# ---------------------------------------------------
# CAN CALCULATOR
# ---------------------------------------------------

elif menu == "CAN Calculator":

    st.header("CAN Bus Load Calculator")

    bitrate = st.number_input(
        "Bitrate (kbps)",
        value=500
    )

    frame_size = st.number_input(
        "Frame Size (bits)",
        value=128
    )

    messages = st.number_input(
        "Messages / Second",
        value=100
    )

    load = (
        frame_size *
        messages
    ) / (
        bitrate * 1000
    )

    st.metric(
        "Bus Load",
        f"{load * 100:.2f}%"
    )

# ---------------------------------------------------
# QUIZ
# ---------------------------------------------------

elif menu == "Quiz":

    st.header("CAN Quiz")

    answer = st.radio(
        "Standard CAN Identifier Length?",
        [
            "8 Bit",
            "11 Bit",
            "16 Bit",
            "29 Bit"
        ]
    )

    if st.button("Submit"):

        if answer == "11 Bit":

            st.success(
                "Correct Answer ✅"
            )

        else:

            st.error(
                "Incorrect ❌"
            )
