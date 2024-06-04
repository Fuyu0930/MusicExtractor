import os
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1


# Create the sql database
def create_database(db_path):
    print("db_path is: ", db_path)
    
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS music_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_location TEXT,
                    music_name TEXT,
                    artist TEXT,
                    album_name TEXT,
                    album_cover_image_location TEXT
                )''')
    connect.commit()
    return connect


# Add information to the database
def database_add(connection, file_path, music_name, artist, album_name, album_cover_image_location, song_id):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO music_info (id, file_location, music_name, artist, album_name, album_cover_image_location) VALUES (?, ?, ?, ?, ?, ?)",
                   (song_id, file_path, music_name, artist, album_name, album_cover_image_location))
    connection.commit()
    

# Extract information, including music name, artist, and album name
def extract_mp3_info(music_file_path, cover_path):
    audio = MP3(music_file_path, ID3=ID3)
    music_name = audio.get('TIT2', TIT2(encoding=3, text="Unknown Title")).text[0]
    artist = audio.get('TPE1', TPE1(encoding=3, text="Unknown Artist")).text[0]
    album_name = audio.get('TALB', TALB(encoding=3, text="Unkown Album")).text[0]

    album_cover_image_location = None
    if audio.tags and 'APIC:' in audio.tags:
        album_cover = audio.tags['APIC:']
        cover_image_path = cover_path + album_name + '.jpg'
        with open(cover_image_path, 'wb') as img:
            img.write(album_cover.data)
        album_cover_image_location = cover_image_path
    
    return music_name, artist, album_name, album_cover_image_location

# Go through each mp3 file in the given folder, and extract information to the sqlite database
def process_handler(music_files, db_path, cover_path):
    connection = create_database(db_path)
    song_id = 0
    for music_file_path in music_files:
        print("Processing file", music_file_path)
        music_name, artist, album_name, album_cover_image_location = extract_mp3_info(music_file_path, cover_path)
        database_add(connection, music_file_path, music_name, artist, album_name, album_cover_image_location, song_id)
        song_id += 1
    
    connection.close()

# A helper function to see all files in the current director
def check_current_directory():
    current_dir = os.getcwd()
    items = os.listdir(current_dir)

    return current_dir, items

def select_output_directory(entry):
    directory = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, directory)

def start_processing():
    if not music_files:
        messagebox.showerror("Error", "No music files")
        return
    
    db_path = db_entry.get() + "/music_database.db"
    cover_path = cover_entry.get() + "/"
    print(cover_path)

    if not db_path or not cover_path:
        messagebox.showerror("Error", "Please set both database and cover directories")
        return

    print("Starting processing")
    print("DB Path:", db_path)
    print("Cover Path:", cover_path)
    print("Music Files:", music_files)

    process_handler(music_files, db_path, cover_path)
    messagebox.showinfo("Success", "Processing completed successfully")

def add_files(event):
    global music_files
    files = root.tk.splitlist(event.data)
    for file in files:
        if file.endswith(".mp3"):
            music_files.append(file)
            file_listbox.insert(tk.END, file)
    print("Files added:", music_files)

if __name__ == "__main__":
    music_files = []
    root = TkinterDnD.Tk()
    root.title("BeatFlow Music Extractor")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    file_listbox = tk.Listbox(frame, width=60, height=10)
    file_listbox.pack(pady=10)
    file_listbox.drop_target_register(DND_FILES)
    file_listbox.dnd_bind('<<Drop>>', add_files)

    # Get the database directory
    db_label = tk.Label(frame, text="Database Directory:")
    db_label.pack(pady=5)
    db_entry = tk.Entry(frame, width=50)
    db_entry.pack(pady=5)
    db_button = tk.Button(frame, text="Browse", command=lambda: select_output_directory(db_entry))
    db_button.pack(pady=5)

    # Get the album cover directory
    cover_label = tk.Label(frame, text="Cover Image Directory:")
    cover_label.pack(pady=5)
    cover_entry = tk.Entry(frame, width=50)
    cover_entry.pack(pady=5)
    cover_button = tk.Button(frame, text="Browse", command=lambda: select_output_directory(cover_entry))
    cover_button.pack(pady=5)

    # Press the button to start the extraction
    process_button = tk.Button(frame, text="Start Processing", command=start_processing)
    process_button.pack(pady=20)

    root.mainloop()