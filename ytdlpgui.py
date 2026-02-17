import sys
import os
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox

def get_bundled_exe_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, "yt-dlp.exe")

def run_ytdlp(url, flags=""):
    ytdlp_path = get_bundled_exe_path()
    
    try:
        subprocess.run(
            [ytdlp_path, flags, url],
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run yt-dlp:\n{e}")

def button_download_video(entry, label_frame):
    url = entry.get().strip()

    if not url:
        return

    start_thread(lambda: run_ytdlp(url), label_frame)

def button_download_audio(entry, label_frame):
    url = entry.get().strip()

    if not url:
        return

    start_thread(lambda: run_ytdlp(url, flags="-f bestaudio"), label_frame)

def start_thread(task_func, label_frame):
    status_label = tk.Label(label_frame, text="Working")
    status_label.grid()

    def task_wrapper():
        task_func()
        status_label.after(0, lambda: status_label.config(text="Done"))
        status_label.after(10000, status_label.destroy)
    
    threading.Thread(target=task_wrapper, daemon=True).start()

def main():
    root = tk.Tk()
    root.title("yt-dlp GUI")
    root.resizable(False, False)

    root.columnconfigure(0, weight=1)

    url_label = tk.Label(root, text="URL:")
    url_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")

    url_entry = tk.Entry(root, width=50)
    url_entry.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="ew")
    url_entry.focus_set()

    button_frame = tk.Frame(root)
    button_frame.grid(row=2, column=0, padx=10, pady=(20, 0), sticky="e")
    button_frame.columnconfigure(0, weight=2)

    status_frame = tk.Frame(root)
    status_frame.grid(row=3, column=0, padx=10, pady=(20, 5), sticky="e")

    download_button = tk.Button(
        button_frame,
        text="Download video",
        command=lambda: button_download_video(url_entry, status_frame),
    )
    download_button.grid(column=0, row=0, padx=(5, 0))

    audio_button = tk.Button(
        button_frame,
        text="Download audio only",
        command=lambda: button_download_audio(url_entry, status_frame),
    )
    audio_button.grid(column=1, row=0, padx=(5, 0))

    root.mainloop()

if __name__ == "__main__":
    main()