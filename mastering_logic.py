import os
import json
import requests
import subprocess
from groq import Groq

# Identity & Environment Setup
TIMESTAMP = os.getenv('MAGE_TIMESTAMP')
SESSION_ID = os.getenv('MAGE_SESSION_ID')
AUDIO_LINK = os.getenv('AUDIO_LINK')
ARTIST = os.getenv('ARTIST')
SONG = os.getenv('SONG')
PRODUCER = os.getenv('PRODUCER')
USER_CMD = os.getenv('USER_COMMAND')

# Live URL Construction
USERNAME = "PopeTroy"
REPO = "celsius-mage-console-pope-troy-signature"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_expert_mastering_math():
    """Analyze Grammy/Billboard winners 1958-2026."""
    system_prompt = (
        "You are a Master Sound Engineer. Analyze Grammy winners 1958-2026. "
        "Provide ONLY a valid FFmpeg filter string. No prose, no quotes."
    )
    user_prompt = f"Master: {SONG} by {ARTIST}. Goal: {USER_CMD}."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.1
        )
        return completion.choices[0].message.content.strip().replace('"', '')
    except:
        return "loudnorm=I=-14:TP=-1.5:LRA=11"

def execute_circuit():
    print(f"--- IGNITING ENGINE: {ARTIST} - {SONG} ---")
    if not AUDIO_LINK:
        print("CRITICAL: No Audio Link found.")
        return
    
    # 1. Download
    r = requests.get(AUDIO_LINK)
    with open("input.wav", "wb") as f:
        f.write(r.content)

    # 2. Expert Math
    math = get_expert_mastering_math()
    print(f"UESP Filter: {math}")

    # 3. Process
    output_name = f"{ARTIST} - {SONG}.mp3"
    cmd = [
        "ffmpeg", "-y", "-i", "input.wav",
        "-af", math,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}",
        "-metadata", f"artist={ARTIST}",
        output_name
    ]
    subprocess.run(cmd)

    # 4. Force Write JSON Registry
    if os.path.exists(output_name):
        url_safe_name = output_name.replace(" ", "%20")
        live_entry = {
            "timestamp": TIMESTAMP,
            "artist": ARTIST,
            "song": SONG,
            "status": "RADIO_READY",
            "download_url": f"{RAW_BASE_URL}{url_safe_name}"
        }
        
        # Explicitly writing to current directory
        json_path = os.path.join(os.getcwd(), 'latest_session.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(live_entry, f, indent=4)
            f.flush()
            os.fsync(f.fileno()) # Forces OS to write to disk
        
        print(f"SUCCESS: JSON written to {json_path}")
    else:
        print("FAILURE: MP3 not created. JSON update skipped.")

if __name__ == "__main__":
    execute_circuit()
