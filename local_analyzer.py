import sqlite3
import librosa
import numpy as np
import os
import warnings

# Ignore librosa's harmless warnings about MP3 fallback decoders
warnings.filterwarnings("ignore")

def setup_database():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # Safely add new columns for our mathematical audio features
    try:
        cursor.execute("ALTER TABLE tracks ADD COLUMN bpm REAL")
        cursor.execute("ALTER TABLE tracks ADD COLUMN energy REAL")
        cursor.execute("ALTER TABLE tracks ADD COLUMN brightness REAL")
        cursor.execute("ALTER TABLE tracks ADD COLUMN local_vibe TEXT")
    except sqlite3.OperationalError:
        pass # Columns already exist
        
    conn.commit()
    return conn

def categorize_vibe(bpm, energy, brightness):
    """A simple algorithmic heuristic to categorize the song's vibe"""
    if energy < 0.05:
        return "Acoustic / Ambient"
    elif bpm > 115 and energy > 0.15:
        return "High Energy / Dance"
    elif bpm < 90 and brightness < 1500:
        return "Late Night / Chill"
    else:
        return "Standard Pop / Rock"

def analyze_local_files(conn):
    cursor = conn.cursor()
    
    # Find tracks that haven't been analyzed yet
    tracks = cursor.execute("SELECT id, title, artist, file_path FROM tracks WHERE bpm IS NULL").fetchall()
    
    print(f"🔬 Found {len(tracks)} tracks to analyze locally...\n")
    
    for track_id, title, artist, file_path in tracks:
        print(f"Analyzing: {title} by {artist}...")
        
        if not os.path.exists(file_path):
            print("  ❌ File missing.")
            continue
            
        try:
            # 1. LOAD AUDIO SNIPPET
            # sr=22050 (standard sample rate), offset=30 (start at 30s), duration=30 (load 30s)
            y, sr = librosa.load(file_path, sr=22050, offset=30.0, duration=30.0)
            
            # 2. EXTRACT TEMPO (BPM)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
            
            # 3. EXTRACT RMS ENERGY (Loudness/Density)
            rms = librosa.feature.rms(y=y)
            energy = float(np.mean(rms))
            
            # 4. EXTRACT SPECTRAL CENTROID (Brightness)
            cent = librosa.feature.spectral_centroid(y=y, sr=sr)
            brightness = float(np.mean(cent))
            
            # 5. CATEGORIZE
            vibe = categorize_vibe(bpm, energy, brightness)
            
            # 6. SAVE TO DATABASE
            cursor.execute('''
                UPDATE tracks 
                SET bpm = ?, energy = ?, brightness = ?, local_vibe = ?
                WHERE id = ?
            ''', (bpm, energy, brightness, vibe, track_id))
            conn.commit()
            
            print(f"  ✅ Done! BPM: {bpm:.0f} | Energy: {energy:.3f} | Vibe: {vibe}")
            
        except Exception as e:
            print(f"  ❌ Error analyzing {file_path}: {e}")

if __name__ == "__main__":
    db_conn = setup_database()
    analyze_local_files(db_conn)
    db_conn.close()
    print("\n🎉 Local audio analysis complete!")