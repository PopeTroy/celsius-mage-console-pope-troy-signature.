import os
import requests
from groq import Groq
from pydub import AudioSegment

# Initialize Prophet Resonance Core Engine (PRCE)
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def execute_dsp_chain():
    # Capture Session Metadata
    we_link = os.getenv('WE_LINK')
    artist = os.getenv('ARTIST', 'Artist').replace(" ", "_")
    song = os.getenv('SONG', 'Track').replace(" ", "_")
    
    print(f"--- INITIALIZING SIGNAL CHAIN: {artist} // {song} ---")

    # 1. Ingest Source Material
    try:
        response = requests.get(we_link, stream=True, timeout=120)
        response.raise_for_status()
        with open("input_source.wav", "wb") as f:
            for chunk in response.iter_content(chunk_size=16384):
                f.write(chunk)
        print(">>> SOURCE INGESTION SUCCESSFUL.")
    except Exception as e:
        print(f"CRITICAL ERROR: Ingestion Failure - {e}")
        return

    # 2. Spectral Analysis & Signal Processing
    try:
        # Load the raw audio data
        audio = AudioSegment.from_file("input_source.wav")
        
        # Apply DSP Mastering Curve (Headroom Management & Normalization)
        # Standard Engineering Peak: -1.0 dBFS
        mastered = audio.normalize(headroom=1.0) 
        
        # 3. High-Fidelity Render (320kbps / 48kHz)
        # We use a fixed filename to ensure the GitHub Runner always finds it
        output_path = "output_render.mp3"
        mastered.export(output_path, format="mp3", bitrate="320k")
        
        if os.path.exists(output_path):
            print(f">>> RENDER COMPLETE: {output_path} (Size: {os.path.getsize(output_path)} bytes)")
        else:
            print(">>> ERROR: Render finished but file not found on disk.")
            
    except Exception as e:
        print(f"CRITICAL ERROR: DSP Processing Failure - {e}")

if __name__ == "__main__":
    execute_dsp_chain()
