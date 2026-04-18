import os
import json
import subprocess
from groq import Groq

# Identity & Environment
TIMESTAMP = os.getenv('MAGE_TIMESTAMP')
ARTIST = os.getenv('ARTIST', 'Unknown Artist')
SONG = os.getenv('SONG', 'New Master')
USER_CMD = os.getenv('USER_COMMAND', 'Expert Master')

USERNAME = "PopeTroy"
REPO = "celsius-mage-console-pope-troy-signature"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_brus_quantum_math():
    """UESP PRCE: Brus-Frequency Mastering Logic."""
    system_prompt = (
        "You are the PRCE Quantum Sound Engineer. Use Brus Equation Logic (d=Bandwidth, Eg=Fundamental, mu=Harmonic Density). "
        "Calculate a 'Blue Shift' for mobile optimization. Provide ONLY a valid FFmpeg filter string. "
        "Use: loudnorm, compand, equalizer, crystalizer. Target -14 LUFS. No prose."
    )
    user_prompt = f"Artist: {ARTIST}. Song: {SONG}. Goal: {USER_CMD}. Apply Nano-Scaling Analysis."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.1
        )
        return completion.choices[0].message.content.strip().replace('"', '').replace('`', '').replace(';', ',')
    except Exception:
        return "loudnorm=I=-14:TP=-1.5:LRA=11"

def execute_circuit():
    print("--- SCANNING FOR RAW SIGNAL ---")
    supported_formats = ('.wav', '.mp3', '.m4a', '.flac')
    input_file = None

    for file in os.listdir('.'):
        if file.lower().endswith(supported_formats) and "master" not in file.lower():
            input_file = file
            break

    if not input_file:
        print("CRITICAL: No input signal.")
        return

    math = get_brus_quantum_math()
    output_name = f"{ARTIST} - {SONG} (Signature Master).mp3"
    
    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-af", math,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}", "-metadata", f"artist={ARTIST}",
        output_name
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["ffmpeg", "-y", "-i", input_file, "-af", "loudnorm=I=-14", "-b:a", "320k", output_name], check=True)

    if os.path.exists(output_name):
        url_safe_name = output_name.replace(" ", "%20")
        live_entry = {
            "timestamp": TIMESTAMP,
            "artist": ARTIST,
            "song": SONG,
            "status": "POPE TROY SIGNATURE MASTER COMPLETE",
            "engine": "PRCE V12 Brus-Frequency",
            "download_url": f"{RAW_BASE_URL}{url_safe_name}"
        }
        with open('latest_session.json', 'w') as f:
            json.dump(live_entry, f, indent=4)

if __name__ == "__main__":
    execute_circuit()
if __name__ == "__main__":
    execute_circuit()
