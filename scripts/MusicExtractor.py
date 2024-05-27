import os
import sqlite3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1


# Extract information, including music name, artist, and album name
def extract_mp3_info(file_path):
    audio = MP3(file_path, ID3=ID3)
    music_name = audio.get('TIT2', TIT2(encoding=3, text="Unknown Title")).text[0]
    artist = audio.get('TPE1', TPE1(encoding=3, text="Unknown Artist")).text[0]
    album_name = audio.get('TALB', TALB(encoding=3, text="Unkown Album")).text[0]

    album_cover_image_location = None
    if audio.tags and 'APIC:' in audio.tags:
        album_cover = audio.tages['APIC:']
        cover_image_path = file_path.replace('.mp3', '.jpg')
        with open(cover_image_path, 'wb') as img:
            img.write(album_cover.data)
        album_cover_image_location = cover_image_path
    
    return music_name, artist, album_name, album_cover_image_location
