import csv
from tkinter import filedialog, messagebox
from lib.localization import get_texts

def export_csv(inbound_data, columns):
    L = get_texts()

    if not inbound_data:
        messagebox.showinfo(L.get("no_data", "No data"), L.get("no_data_to_export", "No data to export"))
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[["CSV files", "*.csv"]])
    if not file_path:
        return

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in inbound_data:
            writer.writerow(row)

    messagebox.showinfo(L.get("export_done", "Export Complete"),
                        f"{L.get('data_saved_to', 'Data saved to')} {file_path}")
