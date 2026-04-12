import os
import json
import requests
import subprocess
from groq import Groq

# Capture Live Environment Variables
TIMESTAMP = os.getenv('MAGE_TIMESTAMP')
SESSION_ID = os.getenv('MAGE_SESSION_ID')
AUDIO_LINK = os.getenv('AUDIO_LINK')
ARTIST = os.getenv('ARTIST')
SONG = os.getenv('SONG')
PRODUCER = os.getenv('PRODUCER')
USER_CMD = os.getenv('USER_COMMAND')

# Live URL Configuration
USERNAME = "PopeTroy"
REPO = "celsius-mage-console-pope-troy-signature"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_overwrite_math():
    """UESP PRCE Engine: Real-time analysis of winners 1958-2026."""
    system_msg = (
        "You are the UESP PRCE Engine. Analyze against Billboard/Grammy winners 1958-2026. "
        "Provide ONLY a valid FFmpeg filter string."
    )
    user_msg = f"Song: {SONG} by {ARTIST}. Goal: {USER_CMD}."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        # High-fidelity fallback math
        return "loudnorm=I=-14:TP=-1.0:LRA=11,firequalizer=gain='if(lt(f,100),-2,if(gt(f,10000),2,0))'"

def execute_circuit():
    print(f"--- IGNITING MAGE ENGINE: {SONG} ---")
    
    if not all([AUDIO_LINK, ARTIST, SONG]):
        print("CRITICAL ERROR: Incomplete Live Data. Aborting.")
        return

    # 1. Download source
    r = requests.get(AUDIO_LINK)
    with open("input.wav", "wb") as f:
        f.write(r.content)

    # 2. Process Master
    math = get_overwrite_math()
    output_name = f"{ARTIST} - {SONG}.mp3"
    
    # -y ensures we overwrite any existing file to prevent hanging
    cmd = [
        "ffmpeg", "-y", "-i", "input.wav",
        "-af", math,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}",
        "-metadata", f"artist={ARTIST}",
        "-metadata", "album_artist=Pope Troy",
        "-metadata", f"composer={PRODUCER}",
        "-metadata", f"comment=Pope Troy Signature Master | UESP PRCE Engine",
        output_name
    ]
    subprocess.run(cmd)
    
    # 3. Finalize Live JSON if file exists
    if os.path.exists(output_name):
        url_safe_name = output_name.replace(" ", "%20")
        live_entry = {
            "timestamp": TIMESTAMP,
            "artist": ARTIST,
            "song": SONG,
            "producer": PRODUCER,
            "session_id": SESSION_ID,
            "status": "RADIO_READY",
            "download_url": f"{RAW_BASE_URL}{url_safe_name}"
        }
        with open('latest_session.json', 'w') as f:
            json.dump(live_entry, f, indent=4)
        print("Success: Live JSON and MP3 generated.")
    else:
        print(f"Error: FFmpeg failed to create {output_name}")

if __name__ == "__main__":
    execute_circuit()
