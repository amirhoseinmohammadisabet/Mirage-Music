import webview
from app import app
import master_engine # Import our new unified engine

def initialize_data(window):
    # This runs as soon as the UI window opens
    try:
        master_engine.run_full_pipeline()
    except Exception as e:
        print(f"Pipeline error: {e}")

if __name__ == '__main__':
    print("Opening Mirage Desktop...")
    
    window = webview.create_window(
        title='Mirage Music', 
        url=app,  
        width=1000, 
        height=750,
        background_color='#121212',
        min_size=(800, 600)
    )
    
    # Start the webview and trigger the background processing
    webview.start(initialize_data, window)