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
        "Use standard filters: loudnorm, compand, equalizer. No quotes, no prose."
    )
    user_prompt = f"Artist: {ARTIST}. Song: {SONG}. Goal: {USER_CMD}."
    
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
    print(f"--- INITIATING SIGNAL: {SONG} ---")
    
    input_file = None
    # Priority 1: Check for manual upload
    for fmt in ['input.mp3', 'input.wav']:
        if os.path.exists(fmt):
            input_file = fmt
            print(f"LOCAL SIGNAL DETECTED: {input_file}")
            break

    # Priority 2: Download if missing
    if not input_file and AUDIO_LINK:
        try:
            r = requests.get(AUDIO_LINK, headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
            input_file = "source_input.mp3"
            with open(input_file, "wb") as f:
                f.write(r.content)
        except:
            return

    if not input_file:
        print("CRITICAL: No input signal found.")
        return

    # 2. Expert Mastering Math
    math = get_expert_mastering_math()
    print(f"UESP Master Chain: {math}")

    # 3. Process with Explicit Format Flag
    output_name = f"{ARTIST} - {SONG}.mp3"
    
    # We use a list to ensure shell arguments are handled safely
    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-af", math,
        "-f", "mp3",  # Force output format to MP3
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}",
        "-metadata", f"artist={ARTIST}",
        output_name
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Fallback to safe master if expert chain is too complex for FFmpeg
    if result.returncode != 0:
        print("Expert Chain failed. Reverting to Safe Winner Curve...")
        fallback_cmd = [
            "ffmpeg", "-y", "-i", input_file,
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-f", "mp3",
            "-codec:a", "libmp3lame", "-b:a", "320k",
            output_name
        ]
        subprocess.run(fallback_cmd, check=True)

    # 4. Finalize Registry
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
        print(f"SUCCESS: {output_name} published.")

if __name__ == "__main__":
    execute_circuit()
            "song": SONG,
            "status": "POPE TROY SIGNATURE MASTER COMPLETE",
            "download_url": f"{RAW_BASE_URL}{url_safe_name}"
        }
        with open('latest_session.json', 'w') as f:
            json.dump(live_entry, f, indent=4)
        print(f"SUCCESS: {output_name} published.")

if __name__ == "__main__":
    execute_circuit()

if __name__ == "__main__":
    execute_circuit()
