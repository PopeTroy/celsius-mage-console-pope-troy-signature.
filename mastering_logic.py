import os
import json
import subprocess
import control as ct
from river import anomaly
from groq import Groq

# Identity & Environment
TIMESTAMP = os.getenv('MAGE_TIMESTAMP')
ARTIST = os.getenv('ARTIST', 'Pope Troy')
SONG = os.getenv('SONG', 'New Master')
USER_CMD = os.getenv('USER_COMMAND', 'Brus-Frequency Master')

USERNAME = "PopeTroy"
REPO = "celsius-mage-console-pope-troy-signature"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
half_space_detector = anomaly.HalfSpaceTrees()

def get_brus_quantum_math():
    """UESP PRCE: Brus-Frequency Mastering Logic."""
    system_prompt = (
        "You are the PRCE Quantum Sound Engineer. Use the Brus Equation to master audio. "
        "Logic: d=Bandwidth, Eg=Fundamental, mu=Harmonic Density. "
        "Provide ONLY a valid FFmpeg filter string using: loudnorm, compand, equalizer. "
        "Target -14 LUFS. No prose."
    )
    user_prompt = f"Artist: {ARTIST}. Song: {SONG}. Goal: {USER_CMD}. Apply Nano-Scaling."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.1
        )
        math = completion.choices[0].message.content.strip()
        return math.replace('"', '').replace('`', '').replace(';', ',')
    except Exception:
        return "loudnorm=I=-14:TP=-1.5:LRA=11"

def execute_circuit():
    print("--- SCANNING FOR RAW SIGNAL ---")
    input_file = next((f for f in os.listdir('.') if f.lower().endswith(('.wav', '.mp3')) and "master" not in f.lower()), None)

    if not input_file:
        print("CRITICAL: Signal Acquisition Failed.")
        return

    half_space_detector.learn_one({'signal_hash': len(ARTIST + SONG)})
    
    math = get_brus_quantum_math()
    output_name = f"{ARTIST} - {SONG} (Signature Master).mp3"
    
    cmd = ["ffmpeg", "-y", "-i", input_file, "-af", math, "-codec:a", "libmp3lame", "-b:a", "320k", output_name]
    
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
            "engine": "PRCE Feedback Loop V12",
            "download_url": f"{RAW_BASE_URL}{url_safe_name}"
        }
        with open('latest_session.json', 'w') as f:
            json.dump(live_entry, f, indent=4)
        print(f"SUCCESS: {output_name} published.")

if __name__ == "__main__":
    execute_circuit()
