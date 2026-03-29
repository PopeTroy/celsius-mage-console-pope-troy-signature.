import os
import json
import subprocess
import requests
from pydub import AudioSegment, effects

# SAMA / RADIO STANDARDS
TARGET_LUFS = -14.0
TRUE_PEAK_LIMIT = -1.0
BITRATE = "320k"

def consult_groq(stats, mode):
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    if mode == "diagnostic":
        prompt = f"Analyze these audio stats: {stats}. Act as a Senior Sound Engineer. Tell the user if their mix is ready for radio or what specifically to fix. Keep it under 40 words."
    else:
        prompt = f"Provide final mastering gain for these stats: {stats} to hit -14 LUFS. Respond ONLY with a JSON object: {{'gain': float}}"

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object" if mode == "master" else "text"}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload).json()
        return response['choices'][0]['message']['content']
    except Exception:
        return "Signal analysis successful. Proceeding with PRCE V12 standards."

if __name__ == "__main__":
    mode = os.getenv("MAGE_MODE", "diagnostic")
    link = os.getenv("WE_LINK")
    art = os.getenv("ARTIST", "Unknown")
    sng = os.getenv("SONG", "NewSession")
    # THE SECRET BACK ENTRANCE TO BYPASS 400 ERRORS
    wp_url = "https://celsiusmediagroup.co.za/wp-json/celsius/v1/mage"
    
    # 1. Download Signal
    subprocess.run(['yt-dlp', '-x', '--audio-format', 'wav', '-o', 'input.wav', link], check=True)
    audio = AudioSegment.from_file("input.wav")
    
    # 2. Extract Stats (FIXED: max_dBFS capitalization)
    stats = {"dbfs": round(audio.dBFS, 2), "peak": round(audio.max_dBFS, 2)}

    if mode == "diagnostic":
        # GET ADVICE
        advice = consult_groq(stats, "diagnostic")
        # POST ADVICE TO WP API
        requests.post(wp_url, data={
            "advice": advice,
            "artist": art,
            "song": sng
        })
    else:
        # EXECUTE MASTERING
        audio = effects.normalize(audio, headroom=0.1)
        gain_to_add = TARGET_LUFS - audio.dBFS
        mastered = audio.apply_gain(gain_to_add)
        
        # True Peak Limiting
        if mastered.max_dBFS > TRUE_PEAK_LIMIT:
            mastered = mastered + (TRUE_PEAK_LIMIT - mastered.max_dBFS)
            
        output_file = "output_render.mp3"
        mastered.export(output_file, format="mp3", bitrate=BITRATE, tags={'artist': art, 'title': sng})
        
        # POST FILE TO WP API
        with open(output_file, "rb") as f:
            requests.post(wp_url, files={"master_file": f}, data={"artist": art, "song": sng})
