from flask import Flask, render_template, jsonify, send_file, request
import sqlite3
import os
import io
import datetime
from mutagen.id3 import ID3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row 
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS listening_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            track_id INTEGER,
            vibe_name TEXT,
            stress_score INTEGER,
            duration_listened REAL
        )
    ''')
    conn.commit()
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tracks')
def get_tracks():
    conn = get_db_connection()
    tracks = conn.execute('SELECT * FROM tracks').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in tracks])

@app.route('/play/<int:track_id>')
def play_track(track_id):
    conn = get_db_connection()
    track = conn.execute('SELECT file_path FROM tracks WHERE id = ?', (track_id,)).fetchone()
    conn.close()
    if track and os.path.exists(track['file_path']):
        return send_file(track['file_path'])
    return "Track not found", 404

@app.route('/cover/<int:track_id>')
def get_cover(track_id):
    conn = get_db_connection()
    track = conn.execute('SELECT file_path FROM tracks WHERE id = ?', (track_id,)).fetchone()
    conn.close()
    if track and os.path.exists(track['file_path']):
        try:
            tags = ID3(track['file_path'])
            for tag in tags.values():
                if tag.FrameID == 'APIC':
                    return send_file(io.BytesIO(tag.data), mimetype=tag.mime)
        except Exception:
            pass 
    return "No cover found", 404

@app.route('/api/queue/<queue_type>/<name>')
def get_mood_queue(queue_type, name):
    conn = get_db_connection()
    name_lower = name.lower()
    
    if queue_type == 'time':
        if name_lower == 'morning': target_mood = 'inspired'
        elif name_lower == 'noon': target_mood = 'joyful'
        elif name_lower == 'afternoon': target_mood = 'relaxed'
        else: target_mood = 'calm'
    else:
        target_mood = name_lower

    # Base query ensures we ONLY sort tracks that have been analyzed
    base_query = 'SELECT * FROM tracks WHERE energy IS NOT NULL'

    # Grab a larger pool (50) of fitting songs, then we will randomize 20 from it
    if target_mood in ['joyful', 'inspired', 'confident']:
        order_clause = 'ORDER BY energy DESC, brightness DESC LIMIT 50'
    elif target_mood in ['grateful', 'calm', 'relaxed']:
        order_clause = 'ORDER BY energy ASC, brightness DESC LIMIT 50'
    elif target_mood in ['gloomy']:
        order_clause = 'ORDER BY energy ASC, brightness ASC LIMIT 50'
    elif target_mood in ['anxious', 'furious']:
        order_clause = 'ORDER BY energy DESC, brightness ASC LIMIT 50'
    else:
        order_clause = 'ORDER BY RANDOM() LIMIT 50'

    # The subquery groups the right mood, the outer query picks 20 randomly so it stays fresh
    query = f"SELECT * FROM ({base_query} {order_clause}) ORDER BY RANDOM() LIMIT 20"

    try:
        tracks = conn.execute(query).fetchall()
        
        # Fallback: If NO tracks have data yet, just play random music
        if not tracks:
            tracks = conn.execute('SELECT * FROM tracks ORDER BY RANDOM() LIMIT 20').fetchall()
            
    except sqlite3.OperationalError:
        tracks = conn.execute('SELECT * FROM tracks ORDER BY RANDOM() LIMIT 20').fetchall()
        
    conn.close()
    display_title = f"CIRCADIAN: {name.title()}" if queue_type == 'time' else f"MOOD: {name.title()}"
    return jsonify({"vibe": display_title, "tracks": [dict(ix) for ix in tracks]})

@app.route('/api/log', methods=['POST'])
def log_telemetry():
    data = request.json
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO listening_logs (timestamp, track_id, vibe_name, stress_score, duration_listened) 
        VALUES (?, ?, ?, ?, ?)
    ''', (
        datetime.datetime.now().isoformat(),
        data.get('track_id'),
        data.get('vibe_name'),
        data.get('stress_score'),
        data.get('duration_listened')
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # 1. Run the basic file scanner to find new MP3s
    import sync_engine
    sync_engine.run_sync()
    
    # 2. Run the heavy DSP engine to calculate real acoustic features
    import dsp_engine
    dsp_engine.run_dsp_sync()
    
    # 3. Start the UI
    app.run(debug=True, port=5000)