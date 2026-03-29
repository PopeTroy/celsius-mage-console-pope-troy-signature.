import os, json, subprocess, requests
from pydub import AudioSegment, effects

TARGET_LUFS = -14.0

def consult_groq(stats, mode):
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    if mode == "diagnostic":
        prompt = f"Stats: {stats}. As a SAMA Engineer, determine if this mix is 'READY' or 'NEEDS_FIX'. Respond ONLY in JSON: {{'status': 'READY'|'NEEDS_FIX', 'advice': 'short critique'}}"
    else:
        prompt = f"Master this mix. Respond ONLY with JSON: {{'gain': float}}"

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        r = requests.post(url, headers=headers, json=payload).json()
        return json.loads(r['choices'][0]['message']['content'])
    except:
        return {"status": "NEEDS_FIX", "advice": "Signal unstable. Manual check required."}

if __name__ == "__main__":
    mode = os.getenv("MAGE_MODE", "diagnostic")
    link = os.getenv("WE_LINK")
    session_id = os.getenv("SESSION_ID")
    wp_url = "https://celsiusmediagroup.co.za/wp-json/celsius/v1/mage"
    
    subprocess.run(['yt-dlp', '-x', '--audio-format', 'wav', '-o', 'input.wav', link], check=True)
    audio = AudioSegment.from_file("input.wav")
    stats = {"dbfs": round(audio.dBFS, 2), "peak": round(audio.max_dBFS, 2)}

    if mode == "diagnostic":
        res = consult_groq(stats, "diagnostic")
        requests.post(wp_url, data={
            "advice": res['advice'], 
            "status": res['status'], 
            "session_id": session_id
        })
    else:
        audio = effects.normalize(audio, headroom=0.1)
        mastered = audio.apply_gain(TARGET_LUFS - audio.dBFS)
        mastered.export("render.mp3", format="mp3", bitrate="320k")
        with open("render.mp3", "rb") as f:
            requests.post(wp_url, files={"master_file": f}, data={"session_id": session_id})
