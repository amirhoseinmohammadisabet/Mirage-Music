# Local Web Music Player

A self-hosted web music player built with Python, Flask, and SQLite. It scans local audio files, extracts metadata, and serves a sleek web UI for streaming.

## Features
- **Local Scanning:** Extracts ID3 tags (Title, Artist, Album, Length) using `mutagen`.
- **Fast Database:** Stores music data in a local SQLite database (`library.db`).
- **Web Interface:** Custom HTML/JS frontend to browse and play music.
- **Audio Streaming:** Uses Flask to securely stream local `.mp3` files to the browser.

## Project Structure
```text
project-folder/
├── Music/                # Directory for your .mp3 files (ignored by Git)
├── templates/
│   └── index.html        # Frontend web interface
├── app.py                # Flask web server and API
├── scanner.py            # MP3 metadata extractor script
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
└── .gitignore            # Git ignore rules