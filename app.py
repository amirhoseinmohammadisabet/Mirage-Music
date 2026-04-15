from flask import Flask, render_template, jsonify, send_file
import sqlite3
import os

app = Flask(__name__)

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('library.db')
    # This line tells SQLite to return data as dictionaries, which is easier for the web
    conn.row_factory = sqlite3.Row 
    return conn

# 1. THE FRONTEND: Serve the main web page
@app.route('/')
def index():
    return render_template('index.html')

# 2. THE API: Send the library data to the web page
@app.route('/api/tracks')
def get_tracks():
    conn = get_db_connection()
    tracks = conn.execute('SELECT * FROM tracks').fetchall()
    conn.close()
    # Convert the SQLite rows into a JSON list
    return jsonify([dict(ix) for ix in tracks])

# 3. THE AUDIO STREAMER: Send the actual MP3 file to the browser
@app.route('/play/<int:track_id>')
def play_track(track_id):
    conn = get_db_connection()
    track = conn.execute('SELECT file_path FROM tracks WHERE id = ?', (track_id,)).fetchone()
    conn.close()
    
    if track and os.path.exists(track['file_path']):
        # send_file streams the audio file safely to the browser
        return send_file(track['file_path'])
    
    return "Track not found", 404

if __name__ == '__main__':
    # Start the server on port 5000
    app.run(debug=True, port=5000)