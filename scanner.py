import os
import sqlite3
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

def setup_database():
    # Connect to SQLite (this creates a file named 'library.db' in your project folder)
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # Create our 'tracks' table if it doesn't already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            artist TEXT,
            album TEXT,
            length INTEGER,
            file_path TEXT UNIQUE
        )
    ''')
    conn.commit()
    return conn

def scan_music_folder(folder_path, conn):
    print(f"Scanning folder: '{folder_path}' and saving to database...\n")
    cursor = conn.cursor()
    songs_added = 0
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                file_path = os.path.join(root, file)
                
                try:
                    audio = MP3(file_path)
                    duration_seconds = int(audio.info.length)
                    tags = EasyID3(file_path)
                    
                    title = tags.get('title', ['Unknown Title'])[0]
                    artist = tags.get('artist', ['Unknown Artist'])[0]
                    album = tags.get('album', ['Unknown Album'])[0]
                    
                    # Save to database. "INSERT OR IGNORE" prevents duplicates 
                    # if you run the script multiple times!
                    cursor.execute('''
                        INSERT OR IGNORE INTO tracks 
                        (title, artist, album, length, file_path) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (title, artist, album, duration_seconds, file_path))
                    
                    # If rowcount > 0, a new song was actually added
                    if cursor.rowcount > 0:
                        print(f"➕ Added: {title} by {artist}")
                        songs_added += 1
                        
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    
    conn.commit()
    print(f"\n✅ Scan complete! {songs_added} new tracks added to the database.")

if __name__ == "__main__":
    db_connection = setup_database()
    scan_music_folder("Music", db_connection)
    db_connection.close()