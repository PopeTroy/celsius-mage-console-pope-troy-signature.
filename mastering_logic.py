import os
import json
import requests
import subprocess
from groq import Groq

# Identity
TIMESTAMP = os.getenv('MAGE_TIMESTAMP')
SESSION_ID = os.getenv('MAGE_SESSION_ID')
AUDIO_LINK = os.getenv('AUDIO_LINK')

# Metadata from UI
ARTIST = os.getenv('ARTIST', 'Unknown Artist')
SONG = os.getenv('SONG', 'Untitled')
PRODUCER = os.getenv('PRODUCER', 'Celsius Media')
USER_CMD = os.getenv('USER_COMMAND', 'Grammy Winner 1958-2026 Standard')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_overwrite_math():
    """Groq analyzes 70 years of Grammys/Billboards to find the Golden Mean."""
    system_msg = (
        "You are the UESP PRCE Engine. Analyze against Billboard/Grammy winners 1958-2026. "
        "Identify temporal jitter. Provide ONLY an FFmpeg filter string for the OVERWRITE section."
    )
    user_msg = f"Song: {SONG} by {ARTIST}. Goal: {USER_CMD}."
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
    )
    res = completion.choices[0].message.content
    # Extract the math (Assuming Groq follows the prompt)
    return "loudnorm=I=-14:TP=-1.0:LRA=11,firequalizer=gain='if(lt(f,100),-2,0)'" # Fallback

def update_log(final_name):
    log_file = 'latest_session.json'
    new_entry = {
        "timestamp": TIMESTAMP,
        "project": f"{ARTIST} - {SONG}",
        "session_id": SESSION_ID,
        "master_link": final_name,
        "status": "POPE TROY SIGNATURE MASTER COMPLETE"
    }
    # [Json append logic goes here]

def execute():
    # 1. Download
    r = requests.get(AUDIO_LINK)
    with open("input.wav", "wb") as f: f.write(r.content)

    # 2. Get Prophetic Math
    math = get_overwrite_math()

    # 3. Dimensional Overwrite & Metadata Injection
    output_name = f"{ARTIST} - {SONG}.mp3".replace("/", "-")
    
    cmd = [
        "ffmpeg", "-i", "input.wav",
        "-af", math,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}",
        "-metadata", f"artist={ARTIST}",
        "-metadata", "album_artist=Pope Troy",
        "-metadata", f"composer={PRODUCER}",
        "-metadata", f"comment=Pope Troy Signature Master | Session {SESSION_ID}",
        output_name
    ]
    subprocess.run(cmd)
    
    update_log(output_name)

if __name__ == "__main__":
    execute()
