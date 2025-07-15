import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk

from lib.fetch import fetch_data, open_settings_window
from lib.export import export_csv
from lib.utils import filter_data, update_table_headers

from lang.en import texts as texts_en, columns_info as columns_en
from lang.ru import texts as texts_ru, columns_info as columns_ru

current_texts = texts_en
current_columns = columns_en

inbound_data = []

def set_language(lang_code):
    global current_texts, current_columns
    if lang_code == 'ru':
        current_texts = texts_ru
        current_columns = columns_ru
        update_table_headers(tree, current_columns)
        current_lang.set('ru')
    else:
        current_texts = texts_en
        current_columns = columns_en
        update_table_headers(tree, current_columns)
        current_lang.set('en')
    update_ui()

def update_ui():
    root.title(current_texts['title'])
    label_search.config(text=current_texts['search_label'])
    btn_connect.config(text=current_texts['connect_button'])
    btn_export.config(text=current_texts['export_button'])
    label_language.config(text=current_texts['language_label'])

root= ThemedTk(theme="breeze")
root.title(current_texts['title'])
root.geometry('930x600')

style= ttk.Style()
style.configure('Treeview', font=('Segoe UI',10), rowheight=28)
style.configure('Treeview.Heading', font=('Segoe UI',11,'bold'))
style.configure('TButton', font=('Segoe UI',10), padding=6)
style.configure('TLabel', font=('Segoe UI',10))
style.configure('TEntry', padding=5)

frame_controls= ttk.Frame(root)
frame_controls.pack(fill='x', padx=10,pady=5)

current_lang = tk.StringVar()
label_language= ttk.Label(frame_controls, text=current_texts['language_label'])
label_language.pack(side='left')

ttk.Radiobutton(
    frame_controls, text='English', variable=current_lang, value='en',
    command=lambda: set_language('en')
).pack(side='left', padx=5)

ttk.Radiobutton(
    frame_controls, text='Русский', variable=current_lang, value='ru',
    command=lambda: set_language('ru')
).pack(side='left', padx=5)

# Поиск
label_search= ttk.Label(frame_controls, text=current_texts['search_label'])
label_search.pack(side='left', padx=(20,5))
entry_search= ttk.Entry(frame_controls,width=30)
entry_search.pack(side='left', padx=5)

# Кнопки
btn_connect= ttk.Button(frame_controls,text=current_texts['connect_button'],
                        command=lambda: fetch_data(tree,inbound_data))
btn_connect.pack(side='right', padx=5)

btn_export= ttk.Button(frame_controls,text=current_texts['export_button'],
                        command=lambda: export_csv(inbound_data, columns))
btn_export.pack(side='right')

settings_btn = ttk.Button(frame_controls, text='⚙️', command=lambda: open_settings_window(root))
settings_btn.pack(side='right', padx=5)

frame_table= ttk.Frame(root)
frame_table.pack(fill='both', expand=True,padx=10,pady=10)

xscroll= ttk.Scrollbar(frame_table,orient='horizontal')
yscroll= ttk.Scrollbar(frame_table,orient='vertical')

tree= ttk.Treeview(frame_table, columns=list(current_columns.keys()), show='headings',
                   xscrollcommand=xscroll.set,
                   yscrollcommand=yscroll.set)

xscroll.config(command=tree.xview)
yscroll.config(command=tree.yview)

tree.pack(side='left', fill='both', expand=True)
yscroll.pack(side='right', fill='y')
xscroll.pack(side='bottom', fill='x')

for col in current_columns:
    tree.heading(col,text=col)
    width = current_columns[col]
    tree.column(col, anchor='center', width=width, stretch=False)

tree.tag_configure('expired', background='#ffcccc')
tree.tag_configure('warning', background='#fff3cd')
tree.tag_configure('active', background='#ccffcc')  

entry_search.bind("<KeyRelease>", lambda e: filter_data(tree,inbound_data,entry_search.get()))

set_language('en')

root.mainloop()