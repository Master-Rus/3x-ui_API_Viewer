import tkinter as tk
from tkinter import ttk
import os
import configparser

from lib.localization import set_language as set_global_language, get_texts

SETTINGS_FILE = 'settings.ini'

def save_language(selected_lang):
    config = configparser.ConfigParser()
    
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)

    if not config.has_section('LANG'):
        config.add_section('LANG')
    
    config.set('LANG', 'language', selected_lang)

    with open(SETTINGS_FILE, 'w') as f:
        config.write(f)

def filter_data(treeview, data_list, keyword):
    keyword = keyword.lower()
    
    for row in treeview.get_children():
        treeview.delete(row)
        
    for row_data in data_list:
        if any(keyword in str(cell).lower() for cell in row_data):
            treeview.insert("", "end", values=row_data)

def update_table_headers(tree, columns):
    tree['columns'] = list(columns.keys())
    
    for col in columns:
        tree.heading(col, text=col, anchor='center')
        tree.column(col, width=columns[col], anchor='center')

L = {}

def select_language():
    global L
    def confirm():
        nonlocal selected_lang
        selected_lang = lang_var.get()
        save_language(selected_lang)
        lang_window.destroy()

    selected_lang = 'en'
    lang_window = tk.Tk()
    lang_window.title("Choose Language / Выберите язык")
    lang_window.geometry("300x150")
    lang_window.resizable(False, False)

    ttk.Label(lang_window, text="Choose language / Выберите язык:", font=('Segoe UI', 10)).pack(pady=10)

    lang_var = tk.StringVar(value='en')
    ttk.Radiobutton(lang_window, text="English", variable=lang_var, value='en').pack()
    ttk.Radiobutton(lang_window, text="Русский", variable=lang_var, value='ru').pack()

    ttk.Button(lang_window, text="OK", command=confirm).pack(pady=10)

    lang_window.mainloop()

    set_global_language(selected_lang)
    L = get_texts()

    return selected_lang
