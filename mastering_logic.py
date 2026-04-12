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
    UESP PRCE: Expert Sound Engineering Analysis.
    Groq analyzes 70 years of Grammy/Billboard winners (1958-2026) 
    to resolve temporal jitter and apply the 'Winner Commonality' curve.
    """
    system_prompt = (
        "You are the UESP PRCE Sound Engineering Engine. You possess the sonic profiles of every "
        "Billboard #1 and Grammy Award-winning song from 1958 to 2026. "
        "Your task: Provide a professional FFmpeg filter string that masters the input audio. "
        "Rules: \n"
        "1. Focus on tonal balance, LUFS normalization (-14), and harmonic clarity.\n"
        "2. Analyze the specific genre/mood requested by the user command.\n"
        "3. Output ONLY the FFmpeg filter string (e.g., 'loudnorm=I=-14,firequalizer=...').\n"
        "4. Do NOT include explanations or quotes."
    )
    
    user_prompt = f"Artist: {ARTIST}. Song: {SONG}. Goal: {USER_CMD}. Producer: {PRODUCER}."
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2 # Keep it precise and technical
        )
        # Ensure the output is clean
        math = completion.choices[0].message.content.strip().replace('"', '').replace('`', '')
        # Fallback security if Groq adds prose
        if "loudnorm" not in math:
            return "loudnorm=I=-14:TP=-1.5:LRA=11,firequalizer=gain='if(lt(f,100),-2,0)'"
        return math
    except Exception as e:
        print(f"UESP Math Error: {e}")
        return "loudnorm=I=-14:TP=-1.5:LRA=11"

def execute_circuit():
    print(f"--- IGNITING EXPERT ENGINE: {ARTIST} - {SONG} ---")
    
    if not all([AUDIO_LINK, ARTIST, SONG]):
        print("CRITICAL: Incomplete Session Data.")
        return

    # 1. Pull the raw signal
    r = requests.get(AUDIO_LINK)
    with open("input.wav", "wb") as f:
        f.write(r.content)

    # 2. Get the Overwrite Math from the Expert Engineer (Groq)
    math = get_expert_mastering_math()
    print(f"Groq Mastering Chain: {math}")

    # 3. Apply the Dimensional Overwrite
    output_name = f"{ARTIST} - {SONG}.mp3"
    
    cmd = [
        "ffmpeg", "-y", "-i", "input.wav",
        "-af", math,
        "-codec:a", "libmp3lame", "-b:a", "320k",
        "-metadata", f"title={SONG}",
        "-metadata", f"artist={ARTIST}",
        "-metadata", f"composer={PRODUCER}",
        "-metadata", "comment=UESP PRCE Signature Master (1958-2026)",
        output_name
    ]
    subprocess.run(cmd)
    
    # 4. Finalize Live Registry
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
        print(f"Master Published: {output_name}")
    else:
        print("Circuit Failed: No file produced.")

if __name__ == "__main__":
    execute_circuit()
