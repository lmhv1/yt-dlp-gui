import os
import sys
import platform
import threading
import subprocess
import validators
import tkinter as tk

def get_bundled_exe_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, "yt-dlp.exe")

def button_download(entry, label_frame, flags=[]):
    url = entry.get().strip()

    start_thread(lambda: run_ytdlp(url, flags), label_frame)

def start_thread(task_func, label_frame):
    def task_wrapper():
        status_label = tk.Label(label_frame, text="Working", wraplength=320)
        status_label.grid()
        out = task_func()
        status_label.after(0, lambda: status_label.config(text=out))
        status_label.after(5000, status_label.destroy)
    
    threading.Thread(target=task_wrapper, daemon=True).start()

def run_ytdlp(url, flags):
    valid = validators.url(url)

    if not url or not valid:
        return "Error: Invalid URL"
    
    ytdlp_path = get_bundled_exe_path()
    
    try:
        result = subprocess.run(
            [ytdlp_path, *flags, url],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        print(f"\n\n\nerror\n{result.stderr}")
        print(f"\n\n\nout\n{result.stdout}")

        out = result.stderr + "\n" + result.stdout
        playlist = False

        for line in out.splitlines():
            if "Downloading playlist" in line:
                playlist = True

            if "Unsupported URL" in line:
                return line

            if any(w in line.lower() for w in (": video unavailable", "error:")):
                return line.split(".", 1)[0]

            if "already been downloaded" in line and not playlist:
                return line.replace("[download] ", "")

            if "Destination" in line and not playlist:
                return f"Downloaded {line.replace("[download] Destination: ", "")}"

            if "Finished downloading playlist" in line:
                return f"Downloaded {line.replace("[download] Finished downloading ", "")}"

        return "Done"
    except Exception as e:
        return "Error: Failed to run yt-dlp", e

def button_folder():
    path = os.path.abspath(".")
    system_name = platform.system()

    if system_name == "Windows":
        subprocess.run(["explorer", path])
    elif system_name == "Darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])

def main():
    root = tk.Tk()
    root.title("yt-dlp GUI")
    root.resizable(False, False)

    # Row 0
    url_frame = tk.Frame(root)
    url_frame.grid(row=0, column=0, padx=10, pady=(5, 0))

    url_label = tk.Label(url_frame, text="URL:")
    url_label.grid(row=0, column=0, sticky="w")

    url_entry = tk.Entry(url_frame, width=50)
    url_entry.grid(row=1, column=0, sticky="ew")
    url_entry.focus_set()

    # Row 1
    button_frame = tk.Frame(root)
    button_frame.grid(row=1, column=0, padx=10, pady=(20, 0), sticky="e")

    folder_button = tk.Button(
        button_frame,
        text="Open folder",
        command=lambda: button_folder(),
    )
    folder_button.grid(row=0, column=0, padx=(5, 0))

    download_button = tk.Button(
        button_frame,
        text="Download video",
        command=lambda: button_download(url_entry, status_frame,
                                        ["--no-warnings", "--no-progress"]),
    )
    download_button.grid(row=0, column=1, padx=(5, 0))

    audio_button = tk.Button(
        button_frame,
        text="Download audio only",
        command=lambda: button_download(url_entry, status_frame,
                                        ["-f bestaudio", "--no-warnings", "--no-progress"]),
    )
    audio_button.grid(row=0, column=2, padx=(5, 0))

    # Row 2
    status_frame = tk.Frame(root)
    status_frame.grid(row=2, column=0, padx=10, pady=(20, 5), sticky="e")

    root.mainloop()

if __name__ == "__main__":
    main()
