import os
import json
import requests
import subprocess
from groq import Groq

# 1. Identity & Environment Setup (Zero Static Defaults)
TIMESTAMP = os.getenv('MAGE_TIMESTAMP')
SESSION_ID = os.getenv('MAGE_SESSION_ID')
AUDIO_LINK = os.getenv('AUDIO_LINK')

# 2. Metadata from Live Payload
ARTIST = os.getenv('ARTIST')
SONG = os.getenv('SONG')
PRODUCER = os.getenv('PRODUCER')
USER_CMD = os.getenv('USER_COMMAND')

# 3. Live URL Construction
USERNAME = "PopeTroy"
REPO = "celsius-mage-console-pope-troy-signature"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_overwrite_math():
    """UESP PRCE Engine analyzes 1958-2026 winners for dimensional commonality."""
    system_msg = (
        "You are the UESP PRCE Engine. Analyze against Billboard/Grammy winners 1958-2026. "
        "Identify temporal jitter. Provide ONLY a valid FFmpeg filter string."
    )
    user_msg = f"Song: {SONG} by {ARTIST}. Goal: {USER_CMD}."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        # High-fidelity fallback math: Commonality Overwrite
        return "loudnorm=I=-14:TP=-1.0:LRA=11,firequalizer=gain='if(lt(f,100),-2,if(gt(f,10000),2,0))'"

def update_live_log(final_filename):
    """Updates the JSON with a live link for WordPress to pull."""
    log_file = 'latest_session.json'
    url_safe_name = final_filename.replace(" ", "%20")
    
    live_entry = {
        "timestamp": TIMESTAMP,
        "artist": ARTIST,
        "song": SONG,
        "producer": PRODUCER,
        "session_id": SESSION_ID,
        "status": "RADIO_READY",
        "download_url": f"{RAW_BASE_URL}{url_safe_name}"
    }

    with open(log_file, 'w') as f:
        json.dump(live_entry, f, indent=4)
    print(f"Live JSON updated: {log_file}")

def execute_circuit():
    print(f"--- IGNITING MAGE ENGINE: {SONG} ---")
    
    if not all([AUDIO_LINK, ARTIST, SONG]):
        print("CRITICAL ERROR: Incomplete Live Data. Aborting.")
        return

    # 1. Download source from Puter
    r = requests.get(AUDIO_LINK)
    with open("input.wav", "wb") as f:
        f.write(r.content)

    # 2. Generate Prophetic Overwrite Math
    math = get_overwrite_math()

    # 3. Apply Dimensional Overwrite & Metadata Injection
    output_name = f"{ARTIST} - {SONG}.mp3"
    
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
    
    # 4. Finalize Live JSON for WordPress
    update_live_log(output_name)

if __name__ == "__main__":
    execute_circuit()
