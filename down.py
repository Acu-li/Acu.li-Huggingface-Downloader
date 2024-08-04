import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
from tkinter import ttk
import sys
from huggingface_hub import snapshot_download, login
import os
from PIL import Image, ImageTk  # Für Bildbearbeitung

# Funktion zum Herunterladen des Modells
def download_model(model_name, download_folder, progress_var, token=None):
    try:
        if token:
            login(token=token)
        # Download des Modells
        snapshot_download(
            repo_id=model_name,
            local_dir=download_folder,
            local_dir_use_symlinks=False,
            revision="main"
        )
        print(f"Model downloaded to {download_folder}")
        # Fortschritt direkt auf 100% setzen, wenn der Download abgeschlossen ist
        progress_var.set(100)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download model: {e}")
        sys.exit(1)

# Funktion zum Ausführen des Downloads in einem separaten Thread
def run_download(model_name, download_folder, progress_var, close_button, token=None):
    def download_with_progress():
        download_model(model_name, download_folder, progress_var, token)

    def update_progress():
        start_time = time.time()
        while progress_var.get() < 100:
            elapsed_time = time.time() - start_time
            if elapsed_time >= 69 * 60:  # 69 Minuten
                if progress_var.get() < 99:
                    progress_var.set(99)
                    messagebox.showinfo("Notice", "Download is a lil slow, check your connection lol")
                break
            if progress_var.get() < 99:
                progress_var.set(progress_var.get() + 1)
            time.sleep(1)  # Alle 1 Sekunde um 1% erhöhen
        # Fortschrittsbalken auf 100% setzen, wenn der Download abgeschlossen ist
        progress_var.set(100)

    def show_close_button():
        while progress_var.get() < 100:
            time.sleep(0.1)
            root.update_idletasks()
        close_button.pack(side=tk.BOTTOM, anchor='se', pady=20, padx=20)
        messagebox.showinfo("Notice", "Download complete")

    threading.Thread(target=download_with_progress).start()
    threading.Thread(target=update_progress).start()
    threading.Thread(target=show_close_button).start()

# Windows 7-Stil für Buttons
def create_button(parent, text, command, width=10):
    button = tk.Button(parent, text=text, command=command, bg="#f0f0f0", fg="#000000", relief='flat', padx=10, pady=5, width=width)
    button.config(borderwidth=1, relief="groove", highlightthickness=1)
    button.pack(padx=5, pady=5)
    return button

# Willkommen-Screen
def welcome_screen():
    welcome_frame = tk.Frame(root, bg="#f0f0f0")
    welcome_frame.pack(fill='both', expand=True)

    # Logo-Bild hinzufügen
    logo_image_path = os.path.join(os.path.dirname(__file__), 'logo.png')
    if os.path.isfile(logo_image_path):
        logo_image = ImageTk.PhotoImage(Image.open(logo_image_path))
        logo_label = tk.Label(welcome_frame, image=logo_image, bg="#f0f0f0")
        logo_label.image = logo_image  # Referenz auf das Bild speichern
        logo_label.place(x=10, y=50)  # Bild etwas weiter nach unten verschieben

    welcome_label = tk.Label(welcome_frame, text="Welcome to Aculi-HF-Downloader", font=("Arial", 16), bg="#f0f0f0", fg="#565656")
    welcome_label.pack(pady=20)

    # Rahmen für die Buttons
    button_frame = tk.Frame(welcome_frame, bg="#f0f0f0")
    button_frame.pack(side=tk.BOTTOM, anchor='se', pady=20, padx=20)

    create_button(button_frame, "Next", lambda: next_screen(welcome_frame))
    create_button(button_frame, "Exit", root.quit)

def next_screen(previous_frame):
    previous_frame.destroy()
    input_frame = tk.Frame(root, bg="#f0f0f0")
    input_frame.pack(fill='both', expand=True)

    folder_label = tk.Label(input_frame, text="Where will the model be downloaded to?", font=("Arial", 12), bg="#f0f0f0", fg="#565656")
    folder_label.pack(pady=10)

    folder_entry = tk.Entry(input_frame, width=50)
    folder_entry.pack(pady=5, padx=20)

    def browse_folder():
        folder_selected = filedialog.askdirectory()
        folder_entry.delete(0, tk.END)  # Vorherigen Inhalt löschen
        folder_entry.insert(0, folder_selected)

    browse_button = create_button(input_frame, "Browse", browse_folder)

    model_label = tk.Label(input_frame, text="Model-Name", font=("Arial", 12), bg="#f0f0f0", fg="#565656")
    model_label.pack(pady=10)

    model_entry = tk.Entry(input_frame, width=50)
    model_entry.pack(pady=5, padx=20)

    token_label = tk.Label(input_frame, text="Read Token (optional)", font=("Arial", 12), bg="#f0f0f0", fg="#565656")
    token_label.pack(pady=10)

    token_entry = tk.Entry(input_frame, width=50)
    token_entry.pack(pady=5, padx=20)

    def start_download():
        model_name = model_entry.get()
        download_folder = folder_entry.get()
        token = token_entry.get()
        if not model_name or not download_folder:
            messagebox.showerror("Error", "Please provide both model name and download folder.")
            return

        input_frame.destroy()
        progress_screen(model_name, download_folder, token)

    button_frame = tk.Frame(input_frame, bg="#f0f0f0")
    button_frame.pack(side=tk.BOTTOM, anchor='se', pady=20, padx=20)

    create_button(button_frame, "Next", start_download)
    create_button(button_frame, "Exit", root.quit)

def progress_screen(model_name, download_folder, token):
    progress_frame = tk.Frame(root, bg="#f0f0f0")
    progress_frame.pack(fill='both', expand=True)

    progress_label = tk.Label(progress_frame, text="Downloading...", font=("Arial", 12), bg="#f0f0f0", fg="#565656")
    progress_label.pack(pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
    progress_bar.pack(pady=10, padx=20, fill='x')

    # Fortschrittsbalken auf lila einstellen
    style = ttk.Style()
    style.configure("TProgressbar", troughcolor='#f0f0f0', background='#A46EBC', thickness=20)

    # Rahmen für die Buttons
    button_frame = tk.Frame(progress_frame, bg="#f0f0f0")
    button_frame.pack(side=tk.BOTTOM, anchor='se', pady=20, padx=20)

    # Close-Button erstellen, aber nicht anzeigen
    close_button = create_button(button_frame, "Close", root.quit)
    close_button.pack_forget()

    run_download(model_name, download_folder, progress_var, close_button, token)

# Hauptanwendung
root = tk.Tk()
root.title("Aculi-HF-Downloader")
root.geometry("400x400")
root.configure(bg="#f0f0f0")

# Setze das Icon des Fensters
icon_path = os.path.join(os.path.dirname(__file__), 'pic-prog.png')
if os.path.isfile(icon_path):
    root.iconphoto(False, tk.PhotoImage(file=icon_path))

welcome_screen()

root.mainloop()
