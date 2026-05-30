import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
import os
from datetime import datetime

# =========================
# UI SETTINGS
# =========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FILE = "cassette_database.csv"

scale = 1.0

# =========================
# COLUMNS
# =========================
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
    "Fault Color",
    "Overall Status",
    "Fault Code",
    "Battery Health",
    "Remarks",
    "Application Area",
    "Current Location"
]

# =========================
# FILE CREATE
# =========================
if not os.path.exists(FILE):
    pd.DataFrame(columns=columns).to_csv(FILE, index=False)

# =========================
# APP WINDOW
# =========================
app = ctk.CTk()
app.title("CASSETTE OPERATION SYSTEM")
app.geometry("1850x920")

# =========================
# FULLSCREEN CONTROL
# =========================
def toggle_fullscreen(event=None):
    app.attributes("-fullscreen", True)

def exit_fullscreen(event=None):
    app.attributes("-fullscreen", False)

app.bind("<F11>", toggle_fullscreen)
app.bind("<Escape>", exit_fullscreen)

# =========================
# ZOOM SYSTEM (WORKING)
# =========================
def apply_zoom():
    global scale

    title.configure(font=("Arial", int(24 * scale), "bold"))

    for c in entries:
        try:
            entries[c].configure(font=("Arial", int(11 * scale)))
        except:
            pass

    style.configure(
        "Treeview",
        font=("Arial", int(10 * scale)),
        rowheight=int(25 * scale)
    )

def zoom_in(event=None):
    global scale
    if scale < 2.0:
        scale += 0.1
        apply_zoom()

def zoom_out(event=None):
    global scale
    if scale > 0.6:
        scale -= 0.1
        apply_zoom()

app.bind("<Control-plus>", zoom_in)
app.bind("<Control-minus>", zoom_out)

# =========================
# HEADER (NO SCADA WORD)
# =========================
header = ctk.CTkFrame(app, fg_color="#050B18", height=90)
header.pack(fill="x")

title = ctk.CTkLabel(
    header,
    text="⚡ SUN MOBILITY | CASSETTE OPERATION SYSTEM ⚡",
    font=("Arial", 24, "bold"),
    text_color="#00E5FF"
)
title.pack(pady=20)

# =========================
# MAIN FRAME
# =========================
main = ctk.CTkFrame(app, fg_color="#0B1220")
main.pack(fill="both", expand=True)

left = ctk.CTkScrollableFrame(main, width=420, fg_color="#111827")
left.pack(side="left", fill="y", padx=10, pady=10)

right = ctk.CTkFrame(main, fg_color="#050B18")
right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# =========================
# INPUTS
# =========================
entries = {}

for i, col in enumerate(columns):

    ctk.CTkLabel(
        left,
        text=col,
        text_color="#38BDF8",
        font=("Arial", 12, "bold")
    ).grid(row=i, column=0, padx=8, pady=5, sticky="w")

    if col == "Fault Color":
        ent = ctk.CTkComboBox(
            left,
            values=["GREEN", "YELLOW", "RED", "WHITE"],
            width=230
        )
        ent.set("GREEN")
    else:
        ent = ctk.CTkEntry(left, width=230)

    ent.grid(row=i, column=1, padx=8, pady=5)
    entries[col] = ent

entries["Date"].insert(0, datetime.now().strftime("%d-%m-%Y"))

# =========================
# SEARCH
# =========================
search_entry = ctk.CTkEntry(
    right,
    placeholder_text="Search Cassette ID",
    width=300
)
search_entry.pack(pady=10)

# =========================
# TABLE
# =========================
table_frame = ctk.CTkFrame(right)
table_frame.pack(fill="both", expand=True)

tree = ttk.Treeview(table_frame, columns=columns, show="headings")

scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)

tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=160, anchor="center")

# =========================
# COLOR TAGS
# =========================
tree.tag_configure("GREEN", background="#16A34A", foreground="white")
tree.tag_configure("YELLOW", background="#EAB308", foreground="black")
tree.tag_configure("RED", background="#DC2626", foreground="white")
tree.tag_configure("WHITE", background="#E5E7EB", foreground="black")

# =========================
# LOAD DATA
# =========================
def load_data(df=None):

    for i in tree.get_children():
        tree.delete(i)

    if df is None:
        df = pd.read_csv(FILE)

    for _, row in df.iterrows():

        color = str(row.get("Fault Color", "WHITE")).upper()
        if color not in ["GREEN", "YELLOW", "RED", "WHITE"]:
            color = "WHITE"

        tree.insert("", "end", values=list(row), tags=(color,))

# =========================
# SAVE
# =========================
def save_data():

    data = {c: entries[c].get() for c in columns}

    if data["Battery Cassette ID"] == "":
        messagebox.showerror("Error", "Cassette ID Required")
        return

    df = pd.read_csv(FILE)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(FILE, index=False)

    load_data()
    messagebox.showinfo("Saved", "Data Stored Successfully")

# =========================
# SEARCH
# =========================
def search_data():

    key = search_entry.get().lower()
    df = pd.read_csv(FILE)

    if key == "":
        load_data(df)
        return

    mask = df.apply(
        lambda r: r.astype(str).str.lower().str.contains(key).any(),
        axis=1
    )

    load_data(df[mask])

# =========================
# DELETE
# =========================
def delete_data():

    sel = tree.selection()

    if not sel:
        messagebox.showwarning("Warning", "Select Record")
        return

    item = tree.item(sel[0])
    cid = item["values"][1]

    df = pd.read_csv(FILE)
    df = df[df["Battery Cassette ID"].astype(str) != str(cid)]
    df.to_csv(FILE, index=False)

    load_data()
    messagebox.showinfo("Deleted", "Record Removed")

# =========================
# CLEAR
# =========================
def clear_data():

    for c in columns:
        entries[c].delete(0, "end")

    entries["Date"].insert(0, datetime.now().strftime("%d-%m-%Y"))

# =========================
# BUTTONS
# =========================
btn_frame = ctk.CTkFrame(right)
btn_frame.pack(fill="x")

buttons = [
    ("SAVE", save_data, "#22C55E"),
    ("SEARCH", search_data, "#3B82F6"),
    ("DELETE", delete_data, "#EF4444"),
    ("CLEAR", clear_data, "#A855F7"),
    ("SHOW ALL", load_data, "#06B6D4")
]

for t, c, col in buttons:
    ctk.CTkButton(
        btn_frame,
        text=t,
        command=c,
        fg_color=col,
        width=140
    ).pack(side="left", padx=5, pady=10)

# =========================
# START
# =========================
load_data()
app.mainloop()