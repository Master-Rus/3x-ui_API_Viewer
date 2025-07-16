import tkinter as tk
import time
from ttkthemes import ThemedTk
from tkinter import ttk

from lib.fetch import fetch_data, open_settings_window
from lib.export import export_csv
from lib.utils import filter_data, update_table_headers, select_language, save_language
from lib.update import ensure_settings_file, check_for_updates_gui, init_language
from lib.localization import set_language as set_global_language, get_texts

from lang.en import columns_info as columns_en
from lang.ru import columns_info as columns_ru

ensure_settings_file()
inbound_data = []

selected = select_language()
set_global_language(selected)
L = get_texts()
init_language()

if selected == 'ru':
    current_columns = columns_ru
    current_lang_code = 'ru'
else:
    current_columns = columns_en
    current_lang_code = 'en'

root = ThemedTk(theme="breeze")
check_for_updates_gui(root)

root.title(L['title'])
root.geometry('950x600')

style = ttk.Style()
style.configure('Treeview', font=('Segoe UI', 10), rowheight=28)
style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'))
style.configure('TButton', font=('Segoe UI', 10), padding=6)
style.configure('TLabel', font=('Segoe UI', 10))
style.configure('TEntry', padding=5)

current_lang = tk.StringVar(value=current_lang_code)

frame_controls = ttk.Frame(root)
frame_controls.pack(fill='x', padx=10, pady=5)

label_language = ttk.Label(frame_controls, text=L['language_label'])
label_language.pack(side='left')

def on_language_change(lang_code):
    global current_columns, L
    set_global_language(lang_code)
    L = get_texts()
    
    if lang_code == 'ru':
        current_columns = columns_ru
        current_lang.set('ru')
    else:
        current_columns = columns_en
        current_lang.set('en')

    save_language(lang_code)
    update_table_headers(tree, current_columns)
    label_search.config(text=L['search_label'])
    btn_connect.config(text=L['connect_button'])
    btn_export.config(text=L['export_button'])
    label_language.config(text=L['language_label'])

for code, label in [('en', 'English'), ('ru', 'Русский')]:
    ttk.Radiobutton(
        frame_controls, text=label, variable=current_lang, value=code,
        command=lambda c=code: on_language_change(c)
    ).pack(side='left', padx=5)

label_search = ttk.Label(frame_controls, text=L['search_label'])
label_search.pack(side='left', padx=(20, 5))
entry_search = ttk.Entry(frame_controls, width=30)
entry_search.pack(side='left', padx=5)

btn_connect = ttk.Button(frame_controls, text=L['connect_button'],
                         command=lambda: fetch_data(tree, inbound_data))
btn_connect.pack(side='right', padx=5)

btn_export = ttk.Button(frame_controls, text=L['export_button'],
                        command=lambda: export_csv(inbound_data, current_columns))
btn_export.pack(side='right')

settings_btn = ttk.Button(frame_controls, text='⚙️', command=lambda: open_settings_window(root))
settings_btn.pack(side='right', padx=5)

frame_table = ttk.Frame(root)
frame_table.pack(fill='both', expand=True, padx=10, pady=10)

xscroll = ttk.Scrollbar(frame_table, orient='horizontal')
yscroll = ttk.Scrollbar(frame_table, orient='vertical')

tree = ttk.Treeview(frame_table, columns=list(current_columns.keys()), show='headings',
                    xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)

xscroll.config(command=tree.xview)
yscroll.config(command=tree.yview)

xscroll.pack(side='bottom', fill='x')
yscroll.pack(side='right', fill='y')
tree.pack(side='left', fill='both', expand=True)

for col in current_columns:
    tree.heading(col, text=col)
    tree.column(col, anchor='center', width=current_columns[col], stretch=False)

tree.tag_configure('expired', background='#ffcccc')
tree.tag_configure('warning', background='#fff3cd')
tree.tag_configure('active', background='#ccffcc')

entry_search.bind("<KeyRelease>", lambda e: filter_data(tree, inbound_data, entry_search.get()))

root.mainloop()
