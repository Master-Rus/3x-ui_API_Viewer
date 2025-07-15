def filter_data(treeview, data_list, keyword):
    keyword= keyword.lower()
    
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