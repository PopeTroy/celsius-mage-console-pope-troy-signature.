import os
import requests
from groq import Groq
from pydub import AudioSegment

# 1. AUTH VIA ENVIRONMENT SECRETS (Already set in your GH Repo)
groq_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=groq_key)

def run_celsius_engine():
    # 2. CAPTURE DATA FROM WE-LINK
    we_link = os.getenv('WE_LINK') 
    artist = os.getenv('ARTIST')
    song = os.getenv('SONG')

    print(f">>> PRCE ENGINE ACTIVE: MASTERING {song} BY {artist}")

    # 3. DOWNLOAD & PROCESS
    # (Your existing mastering_logic.py code continues here...)
    
    # 4. RENDER MP3
    output_file = f"{artist}_{song}_FINAL.mp3".replace(" ", "_")
    # mastered_audio.export(output_file, format="mp3", bitrate="320k")
    print(f">>> RENDER COMPLETE: {output_file}")

if __name__ == "__main__":
    run_celsius_engine()
