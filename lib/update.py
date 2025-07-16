import requests
import os
import zipfile
import shutil
import sys
import time
import configparser
import threading
import tkinter as tk
from tkinter import ttk, messagebox

UPDATE_ZIP_URL = 'https://github.com/Master-Rus/3x-ui_API_Viewer/archive/refs/heads/main.zip'
VERSION_URL = 'https://raw.githubusercontent.com/Master-Rus/3x-ui_API_Viewer/main/version.txt'

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.ini')

def get_language_from_settings():
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
        if config.has_section('LANG') and config.has_option('LANG', 'language'):
            lang = config.get('LANG', 'language').strip().lower()
            #print(f"[DEBUG-update.py] settings.ini: '{lang}'")
            if lang:
                return lang
    return 'en'

def init_language():
    global L
    lang_code = get_language_from_settings()
    if lang_code == 'ru':
        from lang.ru import L as ru_L
        L = ru_L
    else:
        from lang.en import L as en_L
        L = en_L

def ensure_settings_file():
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
    if not config.has_section('UPDATE'):
        config.add_section('UPDATE')
    if not config.has_option('UPDATE', 'version'):
        config.set('UPDATE', 'version', '0.0.0')
    with open(SETTINGS_FILE, 'w') as configfile:
        config.write(configfile)

def get_current_version():
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
    if config.has_section('UPDATE') and config.has_option('UPDATE', 'version'):
        return config.get('UPDATE', 'version')
    return '0.0.0'

def set_current_version(new_version):
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
    if not config.has_section('UPDATE'):
        config.add_section('UPDATE')
    config.set('UPDATE', 'version', new_version)
    with open(SETTINGS_FILE, 'w') as f:
        config.write(f)

def get_latest_version():
    max_attempts = 3
    delay = 2
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(VERSION_URL, timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except Exception:
            pass
        if attempt < max_attempts:
            time.sleep(delay)
    return None

def center_window(parent, window, width, height):
    parent.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def download_update_gui(root, progress_window):
    max_attempts = 3
    delay = 2
    progress_label = progress_window.nametowidget("progress_label")
    attempt_label = progress_window.nametowidget("attempt_label")
    progress_bar = progress_window.nametowidget("progress_bar")

    for attempt in range(1, max_attempts + 1):
        try:
            attempt_label.config(text=L['attempt_label'].format(attempt, max_attempts))
            progress_window.update_idletasks()
            response = requests.get(UPDATE_ZIP_URL, stream=True, timeout=10)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            if response.status_code == 200:
                with open('update.zip', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = int((downloaded / total_size) * 100)
                                progress_bar['value'] = percent
                                progress_label.config(text=L['downloading'].format(percent))
                                progress_window.update_idletasks()
                return True
            else:
                progress_label.config(text=L['http_error'].format(response.status_code))
        except Exception as e:
            progress_label.config(text=L['download_error'].format(e))
        if attempt < max_attempts:
            time.sleep(delay)
    return False

def apply_update_gui(root):
    try:
        with zipfile.ZipFile('update.zip', 'r') as zip_ref:
            temp_dir = 'temp_update'
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            zip_ref.extractall(temp_dir)
            for root_dir, dirs, files in os.walk(temp_dir):
                for file in files:
                    src_file = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(src_file, temp_dir)
                    dst_file = os.path.join(os.getcwd(), rel_path)
                    dst_dir = os.path.dirname(dst_file)
                    if not os.path.exists(dst_dir):
                        os.makedirs(dst_dir)
                    shutil.move(src_file, dst_file)
            shutil.rmtree(temp_dir)
        os.remove('update.zip')
        latest_version = get_latest_version()
        set_current_version(latest_version)
        messagebox.showinfo(L['update'], L['update_success'])
        time.sleep(1)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        messagebox.showerror(L['update_error'], L['apply_update_error'].format(e))

def disable_widgets(widget):
    for child in widget.winfo_children():
        try:
            child.configure(state='disabled')
        except:
            pass
        disable_widgets(child)

def enable_widgets(widget):
    for child in widget.winfo_children():
        try:
            child.configure(state='normal')
        except:
            pass
        enable_widgets(child)

def ask_update_dialog(root, latest_version, current_version):
    dialog = tk.Toplevel(root)
    dialog.title(L['update_available'])
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.transient(root)
    center_window(root, dialog, 300, 150)
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)

    label = ttk.Label(dialog, text=L['update_prompt'].format(latest_version, current_version), justify="center")
    label.pack(pady=20)

    def confirm():
        dialog.grab_release()
        dialog.destroy()
        show_download_progress(root, latest_version)

    def cancel():
        dialog.grab_release()
        dialog.destroy()

    btn_frame = ttk.Frame(dialog)
    btn_frame.pack(pady=10)

    yes_btn = ttk.Button(btn_frame, text=L['yes'], command=confirm)
    yes_btn.pack(side="left", padx=10)

    no_btn = ttk.Button(btn_frame, text=L['no'], command=cancel)
    no_btn.pack(side="right", padx=10)

def show_download_progress(root, latest_version):
    progress_win = tk.Toplevel(root)
    progress_win.title(L['downloading_update'])
    progress_win.resizable(False, False)
    progress_win.grab_set()
    center_window(root, progress_win, 400, 150)

    label_attempt = ttk.Label(progress_win, name="attempt_label", text="")
    label_attempt.pack(pady=(10, 0))

    label_progress = ttk.Label(progress_win, name="progress_label", text=L['starting_download'])
    label_progress.pack(pady=5)

    progress_bar = ttk.Progressbar(progress_win, name="progress_bar", length=300)
    progress_bar.pack(pady=5)

    def threaded_download():
        success = download_update_gui(root, progress_win)
        progress_win.destroy()
        if success:
            apply_update_gui(root)
        else:
            messagebox.showerror(L['update_error'], L['download_failed'])

    threading.Thread(target=threaded_download, daemon=True).start()

def check_for_updates_gui(root):
    def run_update():
        progress_win = tk.Toplevel(root)
        progress_win.title(L['checking_updates'])
        progress_win.resizable(False, False)
        progress_win.grab_set()
        progress_win.protocol("WM_DELETE_WINDOW", lambda: None)
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        center_window(root, progress_win, 350, 100)

        label = tk.Label(progress_win, text=L['checking'])
        label.pack(pady=10)

        progress = ttk.Progressbar(progress_win, length=280, mode="indeterminate")
        progress.pack(pady=5)
        progress.start()

        def close_progress():
            progress.stop()
            progress_win.destroy()
            root.protocol("WM_DELETE_WINDOW", root.destroy)

        try:
            current_version = get_current_version()
            latest_version = None
            max_attempts = 5
            for attempt in range(1, max_attempts + 1):
                label.config(text=L['checking_attempt'].format(attempt, max_attempts))
                root.update_idletasks()
                latest_version = get_latest_version()
                if latest_version:
                    break
                time.sleep(1.5)
            close_progress()
            if not latest_version:
                messagebox.showerror(L['error'], L['check_failed'])
                return
            if latest_version != current_version:
                ask_update_dialog(root, latest_version, current_version)
            else:
                messagebox.showinfo(L['update'], L['no_update'])
        except Exception as e:
            close_progress()
            messagebox.showerror(L['error'], L['check_exception'].format(e))

    threading.Thread(target=run_update, daemon=True).start()
