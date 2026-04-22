import sqlite3
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings

# Ignore scikit-learn memory leak warnings on Windows
warnings.filterwarnings("ignore")

def create_smart_clusters():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # 1. Safely add a column to store the AI's grouping
    try:
        cursor.execute("ALTER TABLE tracks ADD COLUMN cluster_id INTEGER")
    except sqlite3.OperationalError:
        pass 
        
    # 2. Fetch the math data we generated earlier
    tracks = cursor.execute("SELECT id, bpm, energy, brightness FROM tracks WHERE bpm IS NOT NULL").fetchall()
    
    if len(tracks) < 5:
        print("Not enough tracks to find patterns! Run local_analyzer.py on more music first.")
        return

    print(f"🧠 Feeding {len(tracks)} tracks into the K-Means algorithm...")

    track_ids = [t[0] for t in tracks]
    # Format the data into a matrix that the AI can read
    features = np.array([[t[1], t[2], t[3]] for t in tracks])

    # 3. Standardize the data
    # (BPM goes up to 180, but Energy is 0.0 to 1.0. Scaling ensures one metric doesn't overpower the others)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # 4. Apply K-Means Clustering
    # We ask the AI to find exactly 4 distinct "Vibes"
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    labels = kmeans.fit_predict(scaled_features)

    # 5. Save the results back to the database
    for i, track_id in enumerate(track_ids):
        cluster = int(labels[i])
        cursor.execute("UPDATE tracks SET cluster_id = ? WHERE id = ?", (cluster, track_id))
        
    conn.commit()
    conn.close()
    print("✅ Machine Learning complete! Your music is now grouped by actual audio similarity.")

if __name__ == "__main__":
    create_smart_clusters()