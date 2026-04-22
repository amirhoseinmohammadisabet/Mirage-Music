import sqlite3
import random

def inject_mock_data():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # 1. Ensure the mathematical columns actually exist in your database
    try:
        cursor.execute("ALTER TABLE tracks ADD COLUMN energy REAL")
        cursor.execute("ALTER TABLE tracks ADD COLUMN brightness REAL")
        cursor.execute("ALTER TABLE tracks ADD COLUMN bpm REAL")
    except sqlite3.OperationalError:
        pass # If they already exist, just ignore and keep going

    # 2. Get all the tracks currently in your library
    tracks = cursor.execute("SELECT id, title FROM tracks").fetchall()
    
    if len(tracks) == 0:
        print("⚠️ Your database is empty! Run scanner.py first to add MP3s.")
        return
        
    print(f"🔧 Found {len(tracks)} tracks. Injecting simulated acoustic data...")

    # 3. Inject realistic random numbers into every song
    for track in tracks:
        track_id = track[0]
        
        # Energy ranges from 0.0 to 1.0
        energy = round(random.uniform(0.1, 0.99), 3)
        # Brightness (Spectral Centroid) usually ranges from 500 to 3500
        brightness = round(random.uniform(500, 3500), 1)
        # BPM usually ranges from 70 to 170
        bpm = random.randint(70, 170)

        cursor.execute('''
            UPDATE tracks 
            SET energy = ?, brightness = ?, bpm = ?
            WHERE id = ?
        ''', (energy, brightness, bpm, track_id))

    conn.commit()
    conn.close()
    print("✅ Success! Your database is now populated. The mood buttons will now work perfectly.")

if __name__ == '__main__':
    inject_mock_data()