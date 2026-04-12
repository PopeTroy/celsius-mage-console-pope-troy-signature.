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
    """
    UESP PRCE Engine: Analyzing Billboard & Grammy winner commonality (1958-2026).
    """
    system_prompt = (
        "You are a Master Sound Engineer. Analyze the sonic metadata of Grammy-winning tracks "
        "from 1958 to 2026. Provide ONLY a valid FFmpeg filter string for mastering. "
        "Apply the 'Winner Commonality' curve: Tonal balance, -14 LUFS, and high-fidelity clarity. "
        "Output ONLY the string. No prose."
    )
    user_prompt = f"Master this: {SONG} by {ARTIST}. Goal: {USER_CMD}."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.1
        )
        math = completion.choices[0].message.content.strip().replace('"', '').replace('`', '')
        return math if "loudnorm" in math else "loudnorm=I=-14:TP=-1.5:LRA=11"
    except:
        return "loudnorm=I=-14:TP=-1.5:LRA=11"

def execute_circuit():
    if not AUDIO_LINK: return
    
    # 1. Pull the raw signal
    r = requests.get(AUDIO_LINK)
    with open("input.wav", "wb") as f: f.write(r.content)

    # 2. Get Expert Math
    math = get_expert_mastering_math()
    print(f"Prophetic Chain: {math}")

    # 3. Apply Dimensional Overwrite
    # Use simple filename for the process to avoid path errors
    temp_output = "master_output.mp3"
    final_output = f"{ARTIST} - {SONG}.mp3"
    
    cmd = [
        "ffmpeg", "-y", "-i", "input.wav",
        "-af", math,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}",
        "-metadata", f"artist={ARTIST}",
        temp_output
    ]
    subprocess.run(cmd)

    # 4. Finalize & Rename
    if os.path.exists(temp_output):
        os.rename(temp_output, final_output)
        url_safe_name = final_output.replace(" ", "%20")
        live_entry = {
            "timestamp": TIMESTAMP,
            "artist": ARTIST,
            "song": SONG,
            "status": "RADIO_READY",
            "download_url": f"{RAW_BASE_URL}{url_safe_name}"
        }
        with open('latest_session.json', 'w') as f:
            json.dump(live_entry, f, indent=4)
        print(f"UESP Master Success: {final_output}")
    else:
        print("Circuit Failure: FFmpeg did not produce a file.")

if __name__ == "__main__":
    execute_circuit()
            json.dump(live_entry, f, indent=4)
        print(f"Master Published: {output_name}")
    else:
        print("Circuit Failed: No file produced.")

if __name__ == "__main__":
    execute_circuit()
