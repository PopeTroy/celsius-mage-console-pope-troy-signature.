import os
import json
import requests
import subprocess
from groq import Groq

# Identity & Environment
TIMESTAMP = os.getenv('MAGE_TIMESTAMP')
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
    """UESP PRCE: Analysis of Billboard & Grammy Winner Commonality 1958-2026."""
    system_prompt = (
        "You are the UESP PRCE Master Sound Engineer. Analyze winner commonality 1958-2026. "
        "Provide ONLY a valid FFmpeg filter string focusing on tonal balance and -14 LUFS. "
        "Use standard filters: loudnorm, compand, equalizer. No prose, no quotes."
    )
    user_prompt = f"Artist: {ARTIST}. Song: {SONG}. Goal: {USER_CMD}."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.1
        )
        # Sanitize math string to remove any unexpected AI chatter
        math = completion.choices[0].message.content.strip()
        return math.replace('"', '').replace('`', '').replace(';', ',')
    except:
        return "loudnorm=I=-14:TP=-1.5:LRA=11"

def execute_circuit():
    print(f"--- ACQUIRING SIGNAL: {SONG} ---")
    
    input_file = "input.mp3"
    if not os.path.exists(input_file):
        print(f"SIGNAL ERROR: {input_file} not found. Please upload to repo root.")
        return

    # 1. Expert Mastering Math
    math = get_expert_mastering_math()
    print(f"UESP Master Chain: {math}")

    # 2. Apply Dimensional Overwrite
    output_name = f"{ARTIST} - {SONG}.mp3"
    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-af", math,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}",
        "-metadata", f"artist={ARTIST}",
        output_name
    ]
    
    # Run FFmpeg with fallback to safe master
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("Expert Chain failed. Applying Safe Winner Curve...")
        fallback = [
            "ffmpeg", "-y", "-i", input_file,
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-codec:a", "libmp3lame", "-b:a", "320k",
            output_name
        ]
        subprocess.run(fallback, check=True)

    # 3. Finalize & Publish to Registry (Indentation Fixed)
    if os.path.exists(output_name):
        url_safe_name = output_name.replace(" ", "%20")
        live_entry = {
            "timestamp": TIMESTAMP,
            "artist": ARTIST,
            "song": SONG,
            "status": "POPE TROY SIGNATURE MASTER COMPLETE",
            "download_url": f"{RAW_BASE_URL}{url_safe_name}"
        }
        with open('latest_session.json', 'w') as f:
            json.dump(live_entry, f, indent=4)
        print(f"SUCCESS: {output_name} published.")

if __name__ == "__main__":
    execute_circuit()
