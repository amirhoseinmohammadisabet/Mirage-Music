# Smart Clinical Music Player

A full-stack, local-first web application designed for psychoacoustic research. This platform physically analyzes local audio files using Digital Signal Processing (DSP) to dynamically categorize and serve music based on psychological frameworks of mood and circadian rhythms.

## 🔬 Scientific Framework
The application's filtering engine is built upon **Russell’s Circumplex Model of Affect**. Instead of relying on external metadata APIs, the app uses a custom DSP pipeline to extract raw acoustic features from `.mp3` files:
* **Arousal (Energy):** Calculated via Root Mean Square (RMS) energy.
* **Valence (Brightness):** Approximated via Spectral Centroid calculations.

By mapping these mathematical features, the engine can autonomously generate playlists targeting specific affective states (e.g., High Arousal/High Valence for "Joyful", Low Arousal/High Valence for "Calm").

## ✨ Features
* **Local DSP Engine:** Uses `librosa` to analyze soundwaves entirely offline, ensuring absolute privacy and standalone capability.
* **Circadian Auto-Sync:** Implements the clinical *Iso-Principle*, automatically generating playlists designed to entrain the user's cognitive state to the current time of day.
* **Ecological Momentary Assessment (EMA):** Intercepts playback to prompt users for real-time stress/mood check-ins via a UI modal.
* **Telemetry Logging:** Secretly logs all user interactions (track selection, skip rates, listening duration, and self-reported stress scores) into a local SQLite database (`listening_logs` table) for empirical data collection.
* **Cyberpunk/Tech UI:** A fully responsive, glassmorphism-styled frontend.

## 📂 Project Structure
\`\`\`text
project/
├── app.py                # Main Flask web server & routing
├── sync_engine.py        # Boot-sequence: Scans for new MP3s safely
├── dsp_engine.py         # Boot-sequence: Calculates missing acoustic math
├── requirements.txt      # Python dependencies
├── Music/                # Directory for local .mp3 files
├── templates/
│   └── index.html        # Main application UI
└── static/
    ├── style.css         # UI Styling
    ├── script.js         # Frontend playback & telemetry logic
    └── Back.jpg          # UI Background asset
\`\`\`

## 🚀 How to Run
1. Place your `.mp3` files inside the `Music/` directory.
2. Install dependencies: 
   \`pip install -r requirements.txt\`
3. Run the application: 
   \`python app.py\`
   
*Note: The first boot will take a moment as the `dsp_engine.py` physically analyzes the audio waves of any new songs in your folder.*