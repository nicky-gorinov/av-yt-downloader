import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import time
import os
import subprocess
import socket
from PIL import Image, ImageTk

# Global variable to track the last time the progress bar was updated
last_update_time = 0

# Define fonts
larger_font = ("Helvetica", 12)

# Create the main application window using ttkbootstrap
root = ttk.Window(themename="cosmo")
root.title("YouTube Audio and Video Downloader")
root.geometry("600x450")

# Function to load and resize the image with a fixed width and automatic height
def load_image(image_path, width=100):
    image = Image.open(image_path)
    wpercent = (width / float(image.size[0]))
    height = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((width, height), Image.LANCZOS)
    return ImageTk.PhotoImage(image)

# Load the image
image_path = r"C:\Users\nicky\Downloads\wing 1_1_300.png"
loaded_image = load_image(image_path, width=100)

def progress_hook(d):
    global last_update_time
    if d['status'] == 'downloading':
        downloaded = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes', d.get('total_bytes_estimate', 0))
        if total > 0:
            percent = downloaded / total * 100

            current_time = time.time()
            if current_time - last_update_time > 0.1:
                progress_var.set(percent)
                root.update_idletasks()
                last_update_time = current_time

def download_video(url, download_path='.'):
    try:
        ydl_opts_video = {
            'outtmpl': f'{download_path}/%(title)s_video.%(ext)s',
            'format': 'bestvideo[ext=mp4]',
            'noplaylist': True,
            'postprocessors': [],
            'progress_hooks': [progress_hook],
        }

        ydl_opts_audio = {
            'outtmpl': f'{download_path}/%(title)s_audio.%(ext)s',
            'format': 'bestaudio[ext=m4a]',
            'noplaylist': True,
            'postprocessors': [],
            'progress_hooks': [progress_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([url])

        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([url])

        progress_var.set(100)
        messagebox.showinfo("Success", "Download completed successfully!")
        open_folder_button.config(state="normal")

    except (yt_dlp.utils.DownloadError, socket.error) as e:
        if 'm3u8 download detected but ffmpeg could not be found' in str(e):
            messagebox.showerror("Download Error",
                                 "This is a live stream or m3u8 format, which requires ffmpeg. It cannot be downloaded with this tool.")
        else:
            messagebox.showerror("Download Error",
                                 "There was a problem with the download. Please check your Internet connection, YouTube URL and Download Path and try again.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    finally:
        url_entry.config(state="normal")
        path_entry.config(state="normal")
        browse_button.config(state="normal")
        download_button.config(state="normal")

def browse_directory():
    download_path = filedialog.askdirectory()
    if download_path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, download_path)

def start_download():
    url = url_entry.get()
    download_path = path_entry.get()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a valid YouTube URL")
        return
    if not download_path:
        messagebox.showwarning("Input Error", "Please select a download directory")
        return

    url_entry.config(state="disabled")
    path_entry.config(state="disabled")
    browse_button.config(state="disabled")
    download_button.config(state="disabled")

    progress_var.set(0)
    open_folder_button.config(state="disabled")
    threading.Thread(target=download_video, args=(url, download_path)).start()

def open_containing_folder():
    download_path = path_entry.get()
    if os.path.exists(download_path):
        subprocess.Popen(f'explorer "{os.path.realpath(download_path)}"')
    else:
        messagebox.showerror("Error", "The folder path does not exist or is invalid.")

def show_frame(frame):
    frame.tkraise()

# Define style for ttk widgets
style = ttk.Style()
style.configure('TLabel', font=larger_font)
style.configure('TButton', font=larger_font)
style.configure('TEntry', font=larger_font)

# Store references to images to avoid garbage collection
image_references = {}

# Create the frames
main_frame = ttk.Frame(root, padding="20 10 20 10")
about_frame = ttk.Frame(root, padding="20 10 20 10")
how_to_frame = ttk.Frame(root, padding="20 10 20 10")

for frame in (main_frame, about_frame, how_to_frame):
    frame.grid(row=0, column=0, sticky='nsew')

# Add the image to each frame at the top
for frame_name, frame in zip(["main_frame", "about_frame", "how_to_frame"], [main_frame, about_frame, how_to_frame]):
    image_label = ttk.Label(frame, image=loaded_image)

    if frame_name == "main_frame":
        image_label.grid(row=0, column=0, padx=10, pady=(10, 40),
                         sticky="w")  # Extra padding below the image in Main frame
    else:
        image_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")  # Standard padding for other frames

    image_references[frame_name] = loaded_image  # Keep a reference

# Main Frame (Download Interface)
url_label = ttk.Label(main_frame, text="YouTube URL:", bootstyle="info")
url_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
url_entry = ttk.Entry(main_frame, width=50)
url_entry.grid(row=1, column=1, padx=10, pady=10, sticky="we")

path_label = ttk.Label(main_frame, text="Download Path:", bootstyle="info")
path_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
path_entry = ttk.Entry(main_frame, width=50)
path_entry.grid(row=2, column=1, padx=10, pady=10, sticky="we")

browse_button = ttk.Button(main_frame, text="Browse", command=browse_directory, bootstyle="primary")
browse_button.grid(row=2, column=2, padx=10, pady=10, sticky="w")

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100, bootstyle="info")
progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=20, sticky="we")

download_button = ttk.Button(main_frame, text="Download", command=start_download, bootstyle="success")
download_button.grid(row=4, column=1, padx=10, pady=10)

open_folder_button = ttk.Button(main_frame, text="Open Containing Folder", command=open_containing_folder,
                                bootstyle="secondary")
open_folder_button.grid(row=5, column=1, padx=10, pady=10)
open_folder_button.config(state="disabled")

# About Frame
about_label = ttk.Label(about_frame, text="About", font=('Helvetica', 16, 'bold'))
about_label.grid(row=1, column=0, columnspan=3, pady=20)

about_text = ttk.Label(about_frame,
                       text="YouTube Audio and Video Downloader\nVersion 1.0\nDeveloped by GPT4o and N!ck$an\n\nThis application downloads videos and audio separately from YouTube, saving them as two distinct files: .mp4 for video and .m4a for audio.",
                       wraplength=560)
about_text.grid(row=2, column=0, columnspan=3, pady=10)

# The specific part with a different style (e.g., success or warning)
about_text2 = ttk.Label(about_frame,
                        text="Please use downloaded materials responsibly and in accordance with fair use guidelines, respecting copyright laws and the rights of content creators.",
                        bootstyle="warning",  # Change to "warning" if you prefer
                        wraplength=560)
about_text2.grid(row=3, column=0, columnspan=3, pady=(5, 10))  # Padding to separate it from other text


# How To Frame
how_to_label = ttk.Label(how_to_frame, text="How To Use", font=('Helvetica', 16, 'bold'))
how_to_label.grid(row=1, column=0, columnspan=3, pady=20)

how_to_text = ttk.Label(how_to_frame,
                        text="1. Enter the YouTube URL.\n2. Select the download path.\n3. Click 'Download'.\n\nThe app will download both video and audio separately.",
                        wraplength=560)
how_to_text.grid(row=2, column=0, columnspan=3, pady=10)

# Menu Bar
menu_bar = tk.Menu(root)
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Main", command=lambda: show_frame(main_frame))
help_menu.add_command(label="About", command=lambda: show_frame(about_frame))
help_menu.add_command(label="How To", command=lambda: show_frame(how_to_frame))
menu_bar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menu_bar)

# Show the main frame by default
show_frame(main_frame)

# Run the application
root.mainloop()
