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
        response = requests.get(we_link, stream=True, timeout=60)
        response.raise_for_status()
        with open("input_source.wav", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"Critical Ingestion Error: {e}")
        return

    # 2. Spectral Analysis & Normalization
    try:
        audio = AudioSegment.from_file("input_source.wav")
        
        # Applying PRCE Mastering Curve (Normalization to -1.0 dBFS)
        mastered = audio.normalize(headroom=1.0) 
        
        # 3. High-Fidelity Export (320kbps MP3)
        # We save as 'output_render.mp3' to ensure the YML always finds it
        mastered.export("output_render.mp3", format="mp3", bitrate="320k")
        print("--- RENDER COMPLETE: output_render.mp3 ---")
        
    except Exception as e:
        print(f"DSP Processing Failure: {e}")

if __name__ == "__main__":
    execute_dsp_chain()
