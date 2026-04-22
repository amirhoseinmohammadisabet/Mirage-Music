import os
import sqlite3
import numpy as np
import librosa
import warnings
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

# Ignore harmless warnings
warnings.filterwarnings("ignore")

def get_db():
    conn = sqlite3.connect('library.db')
    return conn

def setup_database(conn):
    """Ensures all tables and math columns exist before we start."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, artist TEXT, album TEXT, 
            length INTEGER, file_path TEXT UNIQUE
        )
    ''')
    try:
        cursor.execute("ALTER TABLE tracks ADD COLUMN bpm REAL")
        cursor.execute("ALTER TABLE tracks ADD COLUMN energy REAL")
        cursor.execute("ALTER TABLE tracks ADD COLUMN brightness REAL")
        cursor.execute("ALTER TABLE tracks ADD COLUMN cluster_id INTEGER")
    except sqlite3.OperationalError:
        pass # Columns already exist
    conn.commit()

def step1_scan_folder(conn, folder_path="Music"):
    """Scans for new MP3 files and adds them to the database."""
    print("\n[STEP 1] Scanning for new music...")
    cursor = conn.cursor()
    added = 0
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created '{folder_path}' folder. Drop MP3s here!")
        return

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                file_path = os.path.join(root, file)
                try:
                    audio = MP3(file_path)
                    tags = EasyID3(file_path)
                    title = tags.get('title', ['Unknown'])[0]
                    artist = tags.get('artist', ['Unknown'])[0]
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO tracks 
                        (title, artist, album, length, file_path) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (title, artist, tags.get('album', ['Unknown'])[0], int(audio.info.length), file_path))
                    
                    if cursor.rowcount > 0:
                        added += 1
                except Exception:
                    pass
    conn.commit()
    print(f"✅ Found {added} new tracks.")

def step2_analyze_audio(conn):
    """Calculates BPM, Energy, and Brightness for tracks that are missing data."""
    cursor = conn.cursor()
    tracks = cursor.execute("SELECT id, file_path FROM tracks WHERE bpm IS NULL").fetchall()
    
    if not tracks:
        print("\n[STEP 2] All tracks are already analyzed. Skipping.")
        return

    print(f"\n[STEP 2] Analyzing {len(tracks)} new audio files...")
    for track_id, file_path in tqdm(tracks, desc="Processing Audio"):
        if not os.path.exists(file_path): continue
        try:
            # Load 30 seconds of audio starting at the 30-second mark
            y, sr = librosa.load(file_path, sr=22050, offset=30.0, duration=30.0)
            
            # Math calculations
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
            energy = float(np.mean(librosa.feature.rms(y=y)))
            brightness = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            
            cursor.execute('''
                UPDATE tracks SET bpm = ?, energy = ?, brightness = ? WHERE id = ?
            ''', (bpm, energy, brightness, track_id))
            conn.commit()
            del y # Free memory
        except Exception:
            pass
    print("✅ Audio analysis complete.")

def step3_update_ml_clusters(conn):
    """Regroups all music into smart clusters using Machine Learning."""
    cursor = conn.cursor()
    tracks = cursor.execute("SELECT id, bpm, energy, brightness FROM tracks WHERE bpm IS NOT NULL").fetchall()
    
    if len(tracks) < 5:
        print("\n[STEP 3] Not enough analyzed tracks to run Machine Learning (Need at least 5).")
        return
        
    print("\n[STEP 3] Running Machine Learning clustering...")
    track_ids = [t[0] for t in tracks]
    features = np.array([[t[1], t[2], t[3]] for t in tracks])
    
    # Scale data and group into 4 vibes
    scaled_features = StandardScaler().fit_transform(features)
    labels = KMeans(n_clusters=4, random_state=42, n_init=10).fit_predict(scaled_features)
    
    for i, track_id in enumerate(track_ids):
        cursor.execute("UPDATE tracks SET cluster_id = ? WHERE id = ?", (int(labels[i]), track_id))
    conn.commit()
    print("✅ AI Clustering complete.")

def run_full_pipeline():
    """Runs the entire backend process in order."""
    print("🚀 STARTING MIRAGE MUSIC ENGINE 🚀")
    conn = get_db()
    setup_database(conn)
    step1_scan_folder(conn)
    step2_analyze_audio(conn)
    step3_update_ml_clusters(conn)
    conn.close()
    print("🎉 FULL PIPELINE COMPLETE! App is ready.\n")

if __name__ == "__main__":
    # This allows you to test the engine manually by running: python master_engine.py
    run_full_pipeline()