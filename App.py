import sys
 import socket
 import threading
 import cantools
 import pyqtgraph as pg

from PyQt5.QtCore import Qt, QObject, pyqtSignal
 from PyQt5.QtWidgets import (
 QApplication, QMainWindow, QWidget,import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="Cassette Entry System",
    layout="wide"
)

FILE = "cassette_database.csv"

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
# SAFE FILE INIT
# ==========================

if not os.path.exists(FILE):
    pd.DataFrame(columns=columns).to_csv(FILE, index=False)

# ==========================
# SAFE LOAD
# ==========================

def load_data():
    if os.path.exists(FILE):
        try:
            df = pd.read_csv(FILE)
            return df
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# ==========================
# SAVE RECORD
# ==========================

def save_record(data):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(FILE, index=False)

# ==========================
# DELETE RECORD
# ==========================

def delete_record(cassette_id):
    df = load_data()

    if "Battery Cassette ID" not in df.columns:
        return

    df = df[df["Battery Cassette ID"].astype(str) != str(cassette_id)]
    df.to_csv(FILE, index=False)

# ==========================
# TITLE
# ==========================

st.title("🔋 Cassette Entry System")

tab1, tab2, tab3 = st.tabs([
    "Add Entry",
    "Database",
    "Analytics"
])

# ==========================
# TAB 1 - ADD ENTRY
# ==========================

with tab1:

    st.subheader("Add New Battery Record")

    with st.form("entry_form"):

        data = {}

        col1, col2 = st.columns(2)

        for i, field in enumerate(columns):

            target = col1 if i % 2 == 0 else col2

            with target:

                if field == "Date":
                    data[field] = st.text_input(
                        field,
                        value=datetime.now().strftime("%d-%m-%Y")
                    )

                elif field == "Issue Status":
                    data[field] = st.selectbox(
                        field,
                        ["GREEN", "YELLOW", "RED", "WHITE"]
                    )

                elif field == "Battery Health":
                    data[field] = st.selectbox(
                        field,
                        ["GOOD", "AVERAGE", "CRITICAL"]
                    )

                else:
                    data[field] = st.text_input(field)

        submitted = st.form_submit_button("💾 Save Record")

        if submitted:

            if data["Battery Cassette ID"].strip() == "":
                st.error("Battery Cassette ID Required")

            else:
                save_record(data)
                st.success("Record Saved Successfully")

# ==========================
# TAB 2 - DATABASE
# ==========================

with tab2:

    st.subheader("Database Records")

    df = load_data()

    search = st.text_input("Search Any Value")

    if search:

        mask = df.astype(str).apply(
            lambda row: row.str.contains(search, case=False).any(),
            axis=1
        )

        df = df[mask]

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "📥 Download CSV",
        data=df.to_csv(index=False),
        file_name="cassette_export.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("Delete Record")

    if len(df) > 0:

        cassette = st.selectbox(
            "Select Cassette ID",
            df["Battery Cassette ID"].astype(str).unique()
        )

        if st.button("🗑 Delete"):

            delete_record(cassette)
            st.success(f"{cassette} deleted successfully")
            st.rerun()

# ==========================
# TAB 3 - ANALYTICS
# ==========================

with tab3:

    st.subheader("Analytics Dashboard")

    df = load_data()

    if df.empty:
        st.warning("No Data Available")

    else:

        graph_column = st.selectbox(
            "Select Parameter",
            df.columns
        )

        counts = df[graph_column].astype(str).value_counts()

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.bar(counts.index, counts.values, color="#00BFFF")
        ax.set_title(graph_column)

        plt.xticks(rotation=45)

        st.pyplot(fig)

        st.subheader("Statistics")

        st.write(f"Total Records: {len(df)}")

        if "Issue Status" in df.columns:
            st.write(df["Issue Status"].value_counts())
 QVBoxLayout, QHBoxLayout, QPushButton,
 QFileDialog, QTableWidget, QTableWidgetItem,
 QListWidget, QLabel, QComboBox,
 QTextEdit, QSplitter
 )

HOST = "192.168.0.7"
 PORT = 20001

# ================= SIGNAL BRIDGE =================
 class SignalBridge(QObject):
 update_signal = pyqtSignal(str, float)
 update_trace = pyqtSignal(str)

bridge = SignalBridge()

# ================= TCP THREAD =================
 class TCPClient(threading.Thread):

 def __init__(self, window):
 super().__init__(daemon=True)
 self.window = window
 self.running = True

 def run(self):

 try:
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 sock.connect((HOST, PORT))

 bridge.update_trace.emit(f"Connected to {HOST}:{PORT}")

 while self.running:

 data = sock.recv(8)
 if not data:
 break

 hex_data = data.hex().upper()
 bridge.update_trace.emit(hex_data)

 self.window.decode_can_frame(hex_data)

 except Exception as e:
 bridge.update_trace.emit(str(e))

 def stop(self):
 self.running = False

# ================= MAIN WINDOW =================
 class CANAnalyzer(QMainWindow):

 def __init__(self):
 super().__init__()

 self.db = None
 self.signal_map = {}
 self.plot_map = {}
 self.plot_data = {}

 self.setWindowTitle("CAN Analyzer PRO")
 self.resize(1400, 800)

 root = QWidget()
 self.setCentralWidget(root)
 layout = QVBoxLayout(root)

 # ===== TOP BAR =====
 top = QHBoxLayout()

 self.load_btn = QPushButton("Load DBC")
 self.load_btn.clicked.connect(self.load_dbc)

 self.comm_combo = QComboBox()
 self.comm_combo.addItems(["PEAK PCAN", "RS485", "USR-CANET200"])

 self.connect_btn = QPushButton("Connect")
 self.connect_btn.clicked.connect(self.connect_device)

 top.addWidget(self.load_btn)
 top.addWidget(QLabel("Communication"))
 top.addWidget(self.comm_combo)
 top.addWidget(self.connect_btn)

 layout.addLayout(top)

 # ===== SPLITTER =====
 splitter = QSplitter(Qt.Horizontal)

 # ===== LEFT =====
 left = QWidget()
 left_layout = QVBoxLayout(left)

 left_layout.addWidget(QLabel("Signals"))
 self.signal_list = QListWidget()
 left_layout.addWidget(self.signal_list)

 splitter.addWidget(left)

 # ===== CENTER =====
 center = QWidget()
 center_layout = QVBoxLayout(center)

 self.graph = pg.PlotWidget()
 self.graph.showGrid(x=True, y=True)
 self.graph.setBackground("w")

 center_layout.addWidget(self.graph)

 self.table = QTableWidget()
 self.table.setColumnCount(2)
 self.table.setHorizontalHeaderLabels(["Signal", "Value"])

 center_layout.addWidget(self.table)

 splitter.addWidget(center)

 # ===== RIGHT =====
 right = QWidget()
 right_layout = QVBoxLayout(right)

 self.trace = QTextEdit()
 self.trace.setReadOnly(True)

 right_layout.addWidget(QLabel("Trace"))
 right_layout.addWidget(self.trace)

 splitter.addWidget(right)

 splitter.setSizes([250, 800, 350])
 layout.addWidget(splitter)

 # ===== SIGNALS =====
 bridge.update_signal.connect(self.update_signal)
 bridge.update_trace.connect(self.trace.append)

 self.x_counter = 0
 self.client = None

 # ================= LOAD DBC =================
 def load_dbc(self):

 file_name, _ = QFileDialog.getOpenFileName(self, "Load DBC", "", "*.dbc")
 if not file_name:
 return

 self.db = cantools.database.load_file(file_name)

 self.signal_list.clear()

 for msg in self.db.messages:
 for sig in msg.signals:
 self.signal_list.addItem(sig.name)

 self.trace.append("DBC Loaded Successfully")

 # ================= CONNECT =================
 def connect_device(self):

 mode = self.comm_combo.currentText()
 self.trace.append(f"Connecting: {mode}")

 if mode == "USR-CANET200":
 self.client = TCPClient(self)
 self.client.start()

 elif mode == "PEAK PCAN":
 self.trace.append("PEAK PCAN not implemented yet")

 elif mode == "RS485":
 self.trace.append("RS485 not implemented yet")

 # ================= DECODE CAN =================
 def decode_can_frame(self, hex_data):

 if not self.db:
 return

 try:
 raw = bytes.fromhex(hex_data)

 for msg in self.db.messages:

 try:
 decoded = msg.decode(raw)

 for name, value in decoded.items():
 bridge.update_signal.emit(name, float(value))

 except:
 pass

 except Exception as e:
 bridge.update_trace.emit(f"Decode error: {str(e)}")

 # ================= UPDATE UI =================
 def update_signal(self, signal, value):

 # table update
 if signal not in self.signal_map:

 row = self.table.rowCount()
 self.table.insertRow(row)

 self.table.setItem(row, 0, QTableWidgetItem(signal))
 self.table.setItem(row, 1, QTableWidgetItem(str(value)))

 self.signal_map[signal] = row

 else:
 row = self.signal_map[signal]
 self.table.item(row, 1).setText(str(value))

 # plotting example signals
 if signal in ["PackVoltage", "SOC"]:

 if signal not in self.plot_map:
 self.plot_map[signal] = self.graph.plot(pen=pg.mkPen(width=2))

 self.x_counter += 1

 if signal not in self.plot_data:
 self.plot_data[signal] = {"x": [], "y": []}

 self.plot_data[signal]["x"].append(self.x_counter)
 self.plot_data[signal]["y"].append(value)

 self.plot_map[signal].setData(
 self.plot_data[signal]["x"],
 self.plot_data[signal]["y"]
 )

# ================= MAIN =================
 if __name__ == "__main__":

 app = QApplication(sys.argv)
 win = CANAnalyzer()
 win.show()
 sys.exit(app.exec_())