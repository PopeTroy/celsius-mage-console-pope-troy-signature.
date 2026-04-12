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

USERNAME = "PopeTroy"
REPO = "celsius-mage-console-pope-troy-signature"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_expert_mastering_math():
    """Analyze Billboard/Grammy winners 1958-2026."""
    system_prompt = (
        "You are a Master Sound Engineer. Analyze Grammy winners from 1958 to 2026. "
        "Provide ONLY a valid FFmpeg filter string using standard audio filters: "
        "loudnorm, equalizer, compand, or firequalizer. "
        "Do NOT use 'type=sin' or non-standard experimental parameters. "
        "Output ONLY the string. No prose, no quotes."
    )
    user_prompt = f"Master this: {SONG} by {ARTIST}. Goal: {USER_CMD}."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.1
        )
        return completion.choices[0].message.content.strip().replace('"', '').replace('`', '')
    except:
        return "loudnorm=I=-14:TP=-1.5:LRA=11"

def execute_circuit():
    print(f"--- IGNITING ENGINE: {ARTIST} - {SONG} ---")
    if not AUDIO_LINK:
        print("CRITICAL: No Audio Link.")
        return
    
    # 1. Download and Verify
    try:
        r = requests.get(AUDIO_LINK, timeout=60, stream=True)
        r.raise_for_status()
        with open("input.wav", "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Check if file is large enough to be audio
        if os.path.getsize("input.wav") < 1000:
            print("FAILURE: Downloaded file is too small/invalid.")
            return
    except Exception as e:
        print(f"Download Error: {e}")
        return

    # 2. Engineering Math
    math = get_expert_mastering_math()
    print(f"UESP Master Chain: {math}")

    # 3. Apply Mastering
    output_name = f"{ARTIST} - {SONG}.mp3"
    # Added -ignore_unknown to help with input reading
    cmd = [
        "ffmpeg", "-y", "-i", "input.wav",
        "-af", math,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}",
        "-metadata", f"artist={ARTIST}",
        output_name
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed with math: {math}. Retrying with fallback.")
        fallback_cmd = cmd.copy()
        fallback_cmd[4] = "loudnorm=I=-14:TP=-1.5:LRA=11"
        subprocess.run(fallback_cmd, check=True)

    # 4. JSON Update
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
        print("SUCCESS: Session Logged.")

if __name__ == "__main__":
    execute_circuit()
