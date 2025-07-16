import requests
import configparser
import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from lib.localization import get_texts

SETTINGS_FILE = 'settings.ini'

def load_settings():
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)
    if 'AUTH' not in config:
        config['AUTH'] = {
            'host': 'YouIP/Domain:Port',
            'path': '/YouWebPath',
            'username': 'UserName',
            'password': 'Password',
            'secret': 'SecretKeyPanel'
        }
        with open(SETTINGS_FILE, 'w') as configfile:
            config.write(configfile)
    return config['AUTH']

def save_settings(settings):
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)

    if not config.has_section('AUTH'):
        config.add_section('AUTH')

    for key, value in settings.items():
        config.set('AUTH', key, value)

    with open(SETTINGS_FILE, 'w') as configfile:
        config.write(configfile)

def toggle_visibility_on_focus(entry):
    def on_focus_in(event):
        entry.config(show='')
    def on_focus_out(event):
        entry.config(show='*')
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def open_settings_window(root):
    L = get_texts()
    settings = load_settings()

    settings_win = tk.Toplevel(root)
    settings_window_instance = settings_win
    settings_win.title(L.get("settings_title", "Settings"))
    settings_win.grab_set()

    ttk.Label(settings_win, text=L.get("host", "Host") + ":").grid(row=0, column=0, padx=10, pady=5, sticky='e')

    host_var = tk.StringVar(value=settings.get('host', ''))
    host_entry = ttk.Entry(settings_win, textvariable=host_var, width=50)
    host_entry.grid(row=0, column=1, padx=10, pady=5)
    toggle_visibility_on_focus(host_entry)

    ttk.Label(settings_win, text=L.get("path", "Path") + ":").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    path_var = tk.StringVar(value=settings.get('path', ''))
    path_entry = ttk.Entry(settings_win, textvariable=path_var, width=50, show='*')
    path_entry.grid(row=1, column=1, padx=10, pady=5)
    toggle_visibility_on_focus(path_entry)

    ttk.Label(settings_win, text=L.get("username", "Username") + ":").grid(row=2, column=0, padx=10, pady=5, sticky='e')
    username_var = tk.StringVar(value=settings.get('username', ''))
    username_entry = ttk.Entry(settings_win, textvariable=username_var)
    username_entry.grid(row=2, column=1, padx=10, pady=5)
    toggle_visibility_on_focus(username_entry)

    ttk.Label(settings_win, text=L.get("password", "Password") + ":").grid(row=3,column=0,padx=10,pady=5, sticky='e')
    password_var = tk.StringVar(value=settings.get('password', ''))
    password_entry = ttk.Entry(settings_win,textvariable=password_var,width=30, show='*')
    password_entry.grid(row=3,column=1,padx=10,pady=5)
    toggle_visibility_on_focus(password_entry)

    ttk.Label(settings_win, text=L.get("secret", "Secret") + ":").grid(row=4,column=0,padx=10,pady=5, sticky='e')
    secret_var = tk.StringVar(value=settings.get('secret', ''))
    secret_entry = ttk.Entry(settings_win,textvariable=secret_var,width=50, show='*')
    secret_entry.grid(row=4,column=1,padx=10,pady=5)
    toggle_visibility_on_focus(secret_entry)

    def save():
        new_settings = {
            'host': host_var.get(),
            'path': path_var.get(),
            'username': username_var.get(),
            'password': password_var.get(),
            'secret': secret_var.get()
        }
        save_settings(new_settings)
        messagebox.showinfo(L.get("save", "Save"), L.get("save_success", "Settings saved successfully"))
        settings_win.destroy()

    save_button = ttk.Button(settings_win, text=L.get("save", "Save"), command=save)
    save_button.grid(row=5, columnspan=2, pady=(10, 20))


def fetch_data(tree, inbound_data):
    L = get_texts()
    auth = load_settings()

    host = auth.get("host", "")
    base = auth.get("path", "")
    username = auth.get("username", "")
    password = auth.get("password", "")
    secret = auth.get("secret", "")

    if not all([host, base, username, password]):
        messagebox.showwarning(L.get("fields_required", "Required Fields"), L.get("fill_all_fields", "Please fill all fields in settings."))
        return

    login_url = f"{host}{base}/login"
    inbounds_url = f"{host}{base}/panel/api/inbounds/list"

    session = requests.Session()

    payload = {
        'username': username,
        'password': password
    }
    if secret:
        payload['loginSecret'] = secret

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    try:
        resp = session.post(login_url, data=payload, headers=headers)
        login_data = resp.json()
    except Exception as e:
        messagebox.showerror(L.get("error", "Error"), f"{L.get('auth_error', 'Authentication error')}: {e}")
        return

    if not login_data.get("success"):
        messagebox.showerror(L.get("login_error", "Login Error"), login_data.get("msg", L.get("login_failed", "Login failed")))
        return

    headers_get = {
        'Accept': 'application/json',
        'Referer': f'{host}{base}/xui',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        r = session.get(inbounds_url, headers=headers_get)
        inbounds = r.json()
    except Exception as e:
        messagebox.showerror(L.get("error", "Error"), f"{L.get('fetch_error', 'Error fetching data')}: {e}")
        return

    for row in tree.get_children():
        tree.delete(row)

    inbound_data.clear()

    for inbound in inbounds.get("obj", []):
        port = inbound.get("port")
        protocol = inbound.get("protocol")
        expiry = inbound.get("expiryTime")

        if isinstance(expiry, (int, float)) and expiry > 0:
            expiry_str = datetime.fromtimestamp(expiry / 1000).strftime('%Y-%m-%d')
        else:
            expiry_str = "-"

        enable = "✅" if inbound.get("enable") else "❌"

        stream = inbound.get("streamSettings", {})
        if isinstance(stream, str):
            try:
                stream = json.loads(stream)
            except Exception:
                stream = {}

        reality = stream.get("realitySettings", {})
        domain = reality.get("serverName", "-")
        flow = reality.get("show", "-")
        snip = reality.get("shortId", "-")
        fqdn = reality.get("dest", "-")

        settings_str = inbound.get("settings", "{}")
        try:
            settings_obj = json.loads(settings_str)
            clients = settings_obj.get("clients", [])
        except Exception:
            clients = []

        for client in clients:
            email = client.get("email", "-")
            uuid = client.get("id", "-")
            total_gb = int(client.get("totalGB", 0)) / 1024 / 1024 / 1024
            up_mbps = int(client.get("up", 0)) / 1024 / 1024
            down_mbps = int(client.get("down", 0)) / 1024 / 1024

            total_limit = "Full" if total_gb == 0 else f"{total_gb:.1f} GB"
            traffic_str = f"{up_mbps:.1f} ↑ / {down_mbps:.1f} ↓ MB"

            raw_expiry_ts = client.get("expiryTime") or inbound.get("expiryTime")
            if isinstance(raw_expiry_ts, (int, float)) and raw_expiry_ts > 0:
                end_date_str = datetime.fromtimestamp(raw_expiry_ts / 1000).strftime("%d-%m-%Y %H:%M")
            else:
                end_date_str = "-"

            row_data = [
                email,
                port,
                protocol,
                end_date_str,
                enable,
                total_limit,
                traffic_str
            ]
            inbound_data.append(row_data)

            now_dt = datetime.now()
            try:
                exp_dt_obj = datetime.strptime(end_date_str, "%d-%m-%Y %H:%M")
                delta_days = (exp_dt_obj - now_dt).days
                if delta_days < 0:
                    tag_name = "expired"
                elif delta_days <= 3:
                    tag_name = "warning"
                else:
                    tag_name = "active"
            except Exception:
                tag_name = "active"

            tree.insert("", "end", values=row_data, tags=(tag_name,))
