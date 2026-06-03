import sys
import socket
import threading
import cantools
import pyqtgraph as pg

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import (
 QApplication, QMainWindow, QWidget,
 QVBoxLayout, QHBoxLayout, QPushButton,
 QFileDialog, QTableWidget, QTableWidgetItem,
 QListWidget, QLabel, QComboBox,
 QTextEdit, QSplitter
)

HOST = "192.168.0.7"
PORT = 20001

class SignalBridge(QObject):
 update_signal = pyqtSignal(str, float)
 update_trace = pyqtSignal(str)

bridge = SignalBridge()

class TCPClient(threading.Thread):

 def __init__(self, window):
 super().__init__(daemon=True)
 self.window = window

 def run(self):

 try:
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 sock.connect((HOST, PORT))

 bridge.update_trace.emit(
 f"Connected to {HOST}:{PORT}"
 )

 while True:

 data = sock.recv(1024)

 if not data:
 break

 bridge.update_trace.emit(
 data.hex().upper()
 )

# Dummy values
 bridge.update_signal.emit(
 "PackVoltage",
 650.5
 )

 bridge.update_signal.emit(
 "SOC",
 78.2
 )

 except Exception as e:
 bridge.update_trace.emit(
 str(e)
 )

class CANAnalyzer(QMainWindow):

 def __init__(self):
 super().__init__()

 self.db = None
 self.signal_map = {}

 self.setWindowTitle(
 "CAN Analyzer"
 )

 self.resize(
 1400,
 800
 )

 root = QWidget()
 self.setCentralWidget(root)

 layout = QVBoxLayout(root)

 top = QHBoxLayout()

 self.load_btn = QPushButton(
 "Load DBC"
 )

 self.load_btn.clicked.connect(
 self.load_dbc
 )

 self.comm_combo = QComboBox()

 self.comm_combo.addItems([
 "PEAK PCAN",
 "RS485",
 "USR-CANET200"
 ])

 self.connect_btn = QPushButton(
 "Connect"
 )

 self.connect_btn.clicked.connect(
 self.connect_device
 )

 top.addWidget(self.load_btn)
 top.addWidget(QLabel("Communication"))
 top.addWidget(self.comm_combo)
 top.addWidget(self.connect_btn)

 layout.addLayout(top)

 splitter = QSplitter(
 Qt.Horizontal
 )

# Signal List
 left = QWidget()
 left_layout = QVBoxLayout(left)

 left_layout.addWidget(
 QLabel("Signals")
 )

 self.signal_list = QListWidget()

 left_layout.addWidget(
 self.signal_list
 )

 splitter.addWidget(left)

# Center
 center = QWidget()
 center_layout = QVBoxLayout(center)

 self.graph = pg.PlotWidget()

 self.graph.showGrid(
 x=True,
 y=True
 )

 center_layout.addWidget(
 self.graph
 )

 self.xdata = []
 self.ydata = []

 self.curve = self.graph.plot(
 [],
 []
 )

 self.table = QTableWidget()

 self.table.setColumnCount(2)

 self.table.setHorizontalHeaderLabels(
 ["Signal", "Value"]
 )

 center_layout.addWidget(
 self.table
 )

 splitter.addWidget(center)

# Trace
 right = QWidget()
 right_layout = QVBoxLayout(right)

 self.trace = QTextEdit()

 self.trace.setReadOnly(True)

 right_layout.addWidget(
 QLabel("Trace")
 )

 right_layout.addWidget(
 self.trace
 )

 splitter.addWidget(right)

 splitter.setSizes(
 [250, 800, 350]
 )

 layout.addWidget(splitter)

 bridge.update_signal.connect(
 self.update_signal
 )

 bridge.update_trace.connect(
 self.trace.append
 )

 def load_dbc(self):

 file_name, _ = QFileDialog.getOpenFileName(
 self,
 "Load DBC",
 "",
 "*.dbc"
 )

 if not file_name:
 return

 self.db = cantools.database.load_file(
 file_name
 )

 self.signal_list.clear()

 for msg in self.db.messages:

 for sig in msg.signals:

 self.signal_list.addItem(
 sig.name
 )

 self.trace.append(
 "DBC Loaded"
 )

 def connect_device(self):

 mode = self.comm_combo.currentText()

 self.trace.append(
 f"Connecting: {mode}"
 )

 if mode == "USR-CANET200":
 TCPClient(self).start()

 elif mode == "PEAK PCAN":
 self.trace.append(
 "PEAK support to be added"
 )

 elif mode == "RS485":
 self.trace.append(
 "RS485 support to be added"
 )

 def update_signal(
 self,
 signal,
 value
 ):

 if signal not in self.signal_map:

 row = self.table.rowCount()

 self.table.insertRow(row)

 self.table.setItem(
 row,
 0,
 QTableWidgetItem(signal)
 )

 self.table.setItem(
 row,
 1,
 QTableWidgetItem(str(value))
 )

 self.signal_map[signal] = row

 else:

 row = self.signal_map[signal]

 self.table.item(
 row,
 1
 ).setText(
 str(value)
 )

 if signal == "PackVoltage":

 self.xdata.append(
 len(self.xdata)
 )

 self.ydata.append(
 value
 )

 self.curve.setData(
 self.xdata,
 self.ydata
 )

if __name__ == "__main__":

 app = QApplication(sys.argv)

 win = CANAnalyzer()

 win.show()

 sys.exit(app.exec_())