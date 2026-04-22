import webview
import threading
from app import app # This imports your entire Flask app from app.py!
import time

def start_server():
    # We turn debug=False because this is a "production" desktop app now
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("Starting background server...")
    # 1. Start the Flask server in a background thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True 
    server_thread.start()
    
    # Give the server a split second to boot up before opening the window
    time.sleep(1) 

    print("Opening desktop window...")
    # 2. Create the native desktop window pointing to our local server
    webview.create_window(
        title='Smart Music Player', 
        url='http://127.0.0.1:5000',
        width=1000, 
        height=750,
        background_color='#121212', # Matches our dark theme CSS perfectly
        min_size=(800, 600)
    )
    
    # 3. Start the window (this will keep running until you close the app)
    webview.start()