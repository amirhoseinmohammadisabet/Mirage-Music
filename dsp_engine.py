import sqlite3
import numpy as np
import librosa
import warnings
import os

# Ignore librosa's harmless warnings about MP3 fallback decoders
warnings.filterwarnings("ignore")

def analyze_audio(file_path):
    """Physically analyze the audio waves using librosa."""
    try:
        # Load exactly 30 seconds from the middle of the song. 
        # Analyzing the whole 5-minute file takes too long; 30s is enough for the "vibe".
        y, sr = librosa.load(file_path, sr=22050, offset=30.0, duration=30.0)

        # 1. TEMPO (BPM)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)

        # 2. ENERGY (Arousal) via RMS
        rms = librosa.feature.rms(y=y)
        mean_rms = float(np.mean(rms))
        # Normal RMS values are usually between 0.0 and 0.25. 
        # We mathematically scale this to fit our UI's 0.0 - 1.0 requirement.
        energy_score = min(1.0, mean_rms / 0.25)

        # 3. BRIGHTNESS (Valence) via Spectral Centroid
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        mean_cent = float(np.mean(cent))
        # Normal Centroids range from 500Hz (dark) to 3500Hz (bright).
        # We scale this to fit our UI's 0.0 - 1.0 requirement.
        brightness_score = min(1.0, max(0.0, (mean_cent - 500) / 3000))

        return round(energy_score, 3), round(brightness_score, 3), round(bpm, 1)

    except Exception as e:
        print(f"  [ERROR] Could not analyze {file_path}: {e}")
        return None, None, None

def run_dsp_sync():
    print("[SYSTEM] Booting Digital Signal Processing Engine...")
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Find tracks that have NO acoustic data yet
    unprocessed = cursor.execute("SELECT id, title, file_path FROM tracks WHERE energy IS NULL").fetchall()

    if not unprocessed:
        print("[DSP] All tracks are fully analyzed. Database is perfectly synced.")
        conn.close()
        return

    print(f"[DSP] Starting acoustic analysis on {len(unprocessed)} new tracks.")
    print("        This takes about 1-2 seconds per song depending on your CPU...\n")

    for track_id, title, file_path in unprocessed:
        print(f"  🔬 Analyzing waves: {title}...")
        
        energy, brightness, bpm = analyze_audio(file_path)

        if energy is not None:
            cursor.execute('''
                UPDATE tracks SET energy = ?, brightness = ?, bpm = ? WHERE id = ?
            ''', (energy, brightness, bpm, track_id))
            conn.commit()
            print(f"      -> Energy: {energy} | Brightness: {brightness} | BPM: {bpm}")

    conn.close()
    print("\n[DSP] Audio processing complete! Russell's Circumplex Model is now calibrated.")

if __name__ == '__main__':
    run_dsp_sync()