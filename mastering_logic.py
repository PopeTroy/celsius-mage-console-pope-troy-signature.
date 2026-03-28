import os
import requests
import sys
from groq import Groq
from pydub import AudioSegment

# Initialize Prophet Resonance Core Engine (PRCE)
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def execute_signal_chain():
    # Capture Session Metadata
    we_link = os.getenv('WE_LINK')
    artist = os.getenv('ARTIST', 'Studio_Session').replace(" ", "_")
    song = os.getenv('SONG', 'Master_Render').replace(" ", "_")
    
    print(f"--- INITIALIZING ACOUSTIC INGESTION: {artist} // {song} ---")

    # 1. Source Ingestion
    try:
        response = requests.get(we_link, stream=True, timeout=180)
        response.raise_for_status()
        with open("raw_input.wav", "wb") as f:
            for chunk in response.iter_content(chunk_size=32768):
                f.write(chunk)
        print(">>> SOURCE CAPTURED.")
    except Exception as e:
        print(f"Ingestion Failure: {e}")
        sys.exit(1)

    # 2. Spectral Normalization & DSP Execution
    try:
        # Load data for processing
        audio = AudioSegment.from_file("raw_input.wav")
        
        # Applying PRCE Mastering Curve: Normalization to -0.1 dB Peak
        # This ensures maximum fidelity for streaming standards
        mastered = audio.normalize(headroom=0.1) 
        
        # 3. High-Fidelity Signal Export
        # Explicitly define the export to ensure the runner detects it
        output_file = "output_render.mp3"
        
        # Rendering at 320kbps / 48kHz / Stereo
        mastered.export(
            output_file, 
            format="mp3", 
            bitrate="320k", 
            parameters=["-ar", "48000"]
        )
        
        if os.path.exists(output_file):
            print(f">>> DSP RENDER SUCCESS: {output_file} ({os.path.getsize(output_file)} bytes)")
        else:
            print(">>> CRITICAL ERROR: Render path empty post-export.")
            sys.exit(1)
            
    except Exception as e:
        print(f"DSP Signal Failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    execute_signal_chain()
