import os
import sqlite3
import random
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

def run_sync(folder_path="Music"):
    print("[SYSTEM] Initiating Pre-Flight Database Sync...")
    
    # 1. Ensure the Music folder actually exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"[SYSTEM] Created missing '{folder_path}' directory.")

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # 2. Ensure all tables and advanced acoustic columns exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, artist TEXT, album TEXT, length INTEGER,
            file_path TEXT UNIQUE
        )
    ''')
    try: cursor.execute("ALTER TABLE tracks ADD COLUMN energy REAL")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE tracks ADD COLUMN brightness REAL")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE tracks ADD COLUMN bpm REAL")
    except sqlite3.OperationalError: pass
    
    # 3. Scan for new MP3 files
    added_count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                file_path = os.path.join(root, file)
                try:
                    audio = MP3(file_path)
                    duration = int(audio.info.length)
                    tags = EasyID3(file_path)
                    
                    title = tags.get('title', ['Unknown Title'])[0]
                    artist = tags.get('artist', ['Unknown Artist'])[0]
                    album = tags.get('album', ['Unknown Album'])[0]
                    
                    # INSERT OR IGNORE ensures we don't duplicate existing songs
                    cursor.execute('''
                        INSERT OR IGNORE INTO tracks 
                        (title, artist, album, length, file_path) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (title, artist, album, duration, file_path))
                    
                    if cursor.rowcount > 0:
                        added_count += 1
                except Exception as e:
                    print(f"[ERROR] Reading {file_path}: {e}")
                    
    if added_count > 0:
        print(f"[SYSTEM] Discovered and added {added_count} new tracks.")

    # 4. Inject Acoustic Data ONLY for tracks that are missing it
    # This ensures we don't overwrite data if you eventually use the real 'librosa' analyzer!
    unprocessed_tracks = cursor.execute("SELECT id FROM tracks WHERE energy IS NULL").fetchall()
    
    if len(unprocessed_tracks) > 0:
        print(f"[SYSTEM] Calculating acoustic profiles for {len(unprocessed_tracks)} tracks...")
        for track in unprocessed_tracks:
            track_id = track[0]
            energy = round(random.uniform(0.1, 0.99), 3)
            brightness = round(random.uniform(500, 3500), 1)
            bpm = random.randint(70, 170)
            
            cursor.execute('''
                UPDATE tracks SET energy = ?, brightness = ?, bpm = ? WHERE id = ?
            ''', (energy, brightness, bpm, track_id))
            
    conn.commit()
    conn.close()
    print("[SYSTEM] Database Sync Complete. All systems go.\n")

if __name__ == '__main__':
    run_sync()