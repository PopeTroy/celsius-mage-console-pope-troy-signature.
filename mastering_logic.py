import os
import json
import requests
import subprocess
from groq import Groq

# Identity & Environment (Zero Static Defaults)
TIMESTAMP = os.getenv('MAGE_TIMESTAMP')
SESSION_ID = os.getenv('MAGE_SESSION_ID')
AUDIO_LINK = os.getenv('AUDIO_LINK')
ARTIST = os.getenv('ARTIST')
SONG = os.getenv('SONG')
PRODUCER = os.getenv('PRODUCER')
USER_CMD = os.getenv('USER_COMMAND')

USERNAME = "PopeTroy"
REPO = "celsius-mage-console-pope-troy-signature"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_overwrite_math():
    system_msg = "You are the UESP PRCE Engine. Provide ONLY a valid FFmpeg filter string."
    user_msg = f"Song: {SONG} by {ARTIST}. Goal: {USER_CMD}."
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
        )
        return completion.choices[0].message.content.strip()
    except:
        return "loudnorm=I=-14:TP=-1.0:LRA=11"

def execute():
    if not AUDIO_LINK: return
    
    # Download
    r = requests.get(AUDIO_LINK)
    with open("input.wav", "wb") as f: f.write(r.content)

    # Process
    math = get_overwrite_math()
    output_name = f"{ARTIST} - {SONG}.mp3"
    
    # -y forces overwrite to avoid hanging
    cmd = [
        "ffmpeg", "-y", "-i", "input.wav",
        "-af", math,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}",
        "-metadata", f"artist={ARTIST}",
        output_name
    ]
    subprocess.run(cmd)

    # FINAL CHECK: Ensure file was created
    if os.path.exists(output_name):
        url_safe_name = output_name.replace(" ", "%20")
        live_entry = {
            "timestamp": TIMESTAMP,
            "artist": ARTIST,
            "song": SONG,
            "status": "RADIO_READY",
            "download_url": f"{RAW_BASE_URL}{url_safe_name}"
        }
        with open('latest_session.json', 'w') as f:
            json.dump(live_entry, f, indent=4)
    else:
        print(f"Error: {output_name} was not created by FFmpeg.")

if __name__ == "__main__":
    execute()
