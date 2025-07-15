import csv
from tkinter import filedialog, messagebox

def export_csv(inbound_data, columns):
    if not inbound_data:
        messagebox.showinfo("Нет данных", "Нет данных для экспорта")
        return

    file_path= filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[["CSV files","*.csv"]])
    if not file_path:
        return

    with open(file_path,"w", newline="", encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(columns)
        for row in inbound_data:
            writer.writerow(row)
    
    messagebox.showinfo("Экспорт завершён", f"Данные сохранены в {file_path}")