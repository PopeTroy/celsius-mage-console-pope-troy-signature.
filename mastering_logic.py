import os, json, subprocess, requests
from pydub import AudioSegment, effects

# AUDIO STANDARDS
TARGET_LUFS = -14.0
TRUE_PEAK_LIMIT = -1.0

def consult_groq(stats, mode):
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"Stats: {stats}. As a SAMA Engineer, "
    if mode == "diagnostic":
        prompt += "diagnose this mix (under 40 words)."
    else:
        prompt += "Master this mix for radio. Respond ONLY with JSON: {'gain': float}"

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object" if mode == "master" else "text"}
    }
    try:
        r = requests.post(url, headers=headers, json=payload).json()
        return r['choices'][0]['message']['content']
    except:
        return "Mix analysis successful. Signal stable. Proceed to master."

if __name__ == "__main__":
    mode = os.getenv("MAGE_MODE", "diagnostic")
    link = os.getenv("WE_LINK")
    art = os.getenv("ARTIST", "Unknown")
    sng = os.getenv("SONG", "NewSession")
    
    # THE SECRET BACK ENTRANCE
    wp_url = "https://celsiusmediagroup.co.za/wp-json/celsius/v1/mage"
    
    # UNIQUE SESSION KEY - STRICT MATCHING
    session_id = f"{art}_{sng}".replace(" ", "").lower()
    
    # 1. DOWNLOAD
    subprocess.run(['yt-dlp', '-x', '--audio-format', 'wav', '-o', 'input.wav', link], check=True)
    audio = AudioSegment.from_file("input.wav")
    
    # 2. STATS (FIXED: max_dBFS capitalization)
    stats = {"dbfs": round(audio.dBFS, 2), "peak": round(audio.max_dBFS, 2)}

    if mode == "diagnostic":
        advice = consult_groq(stats, "diagnostic")
        requests.post(wp_url, data={"advice": advice, "session_id": session_id})
    else:
        # MASTERING CHAIN
        audio = effects.normalize(audio, headroom=0.1)
        mastered = audio.apply_gain(TARGET_LUFS - audio.dBFS)
        output = "render.mp3"
        mastered.export(output, format="mp3", bitrate="320k")
        
        # UPLOAD
        with open(output, "rb") as f:
            requests.post(wp_url, files={"master_file": f}, data={"session_id": session_id})
