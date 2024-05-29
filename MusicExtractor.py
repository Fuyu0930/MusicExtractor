import os
import sqlite3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1


# Create the sql database
def create_database(db_path):
    print("db_path is: ", db_path)
    
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS music_info (
                    file_location TEXT,
                    music_name TEXT,
                    artist TEXT,
                    album_name TEXT,
                    album_cover_image_location TEXT
                )''')
    connect.commit()
    return connect


# Add information to the database
def database_add(connection, file_path, music_name, artist, album_name, album_cover_image_location):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO music_info (file_location, music_name, artist, album_name, album_cover_image_location) VALUES (?, ?, ?, ?, ?)",
                   (file_path, music_name, artist, album_name, album_cover_image_location))
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
        cover_image_path = cover_path + (music_file_path.replace('.mp3', '.jpg')).split('/')[-1]
        with open(cover_image_path, 'wb') as img:
            img.write(album_cover.data)
        album_cover_image_location = cover_image_path
    
    return music_name, artist, album_name, album_cover_image_location

# Go through each mp3 file in the given folder, and extract information to the sqlite database
def process_handler(music_path, db_path, cover_path):
    connection = create_database(db_path)
    for root, _, files in os.walk(music_path):
        for file in files:
            if file.endswith(".mp3"):
                music_file_path = os.path.join(root, file)
                music_name, artist, album_name, album_cover_image_location = extract_mp3_info(music_file_path, cover_path)
                database_add(connection, music_file_path, music_name, artist, album_name, album_cover_image_location)
    connection.close()

# A helper function to see all files in the current director
def check_current_directory():
    current_dir = os.getcwd()
    items = os.listdir(current_dir)

    return current_dir, items

if __name__ == "__main__":
    # Check the current directory
    current_dir, items = check_current_directory()
    print(f"Current Directory: {current_dir}")
    print("Items:")
    for item in items:
        print(f"-{item}")
    
    # Define paths and call the handler function
    music_path = "music/"
    db_path = "database/music_database.db"
    cover_path = "covers/"
    process_handler(music_path, db_path, cover_path)