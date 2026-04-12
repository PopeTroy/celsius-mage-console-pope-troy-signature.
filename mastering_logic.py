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
        "Provide ONLY a valid FFmpeg filter string. Focus on tonal balance and -14 LUFS. "
        "Standard filters ONLY: loudnorm, compand, equalizer. No prose."
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
    print(f"--- ACQUIRING SIGNAL: {SONG} ---")
    
    # 1. High-Precision Signal Acquisition
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(AUDIO_LINK, headers=headers, timeout=60)
        r.raise_for_status()
        
        # Determine format and detect HTML poison
        content_type = r.headers.get('Content-Type', '').lower()
        if 'text/html' in content_type:
            print("CRITICAL: The link provided is a web page, not a direct audio file.")
            return

        source_ext = "wav" if ".wav" in AUDIO_LINK.lower() else "mp3"
        input_filename = f"source_input.{source_ext}"
        
        with open(input_filename, "wb") as f:
            f.write(r.content)
            
        if os.path.getsize(input_filename) < 20000: # Files under 20KB are almost never audio
            print("SIGNAL ERROR: File size too small. Likely an error page or redirect.")
            return
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        return

    # 2. Expert Mastering Math
    math = get_expert_mastering_math()
    print(f"UESP Master Chain: {math}")

    # 3. Apply Dimensional Overwrite
    output_name = f"{ARTIST} - {SONG}.mp3"
    cmd = [
        "ffmpeg", "-y", "-i", input_filename,
        "-af", math,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}",
        "-metadata", f"artist={ARTIST}",
        output_name
    ]
    
    # Run with fallback logic
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Expert Chain failed (Exit 183/234). Applying Safe Winner Curve...")
        cmd[4] = "loudnorm=I=-14:TP=-1.5:LRA=11"
        subprocess.run(cmd, check=True)

    # 4. Finalize & Publish to Registry
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
