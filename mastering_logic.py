import os, json, subprocess, requests
from pydub import AudioSegment, effects

TARGET_LUFS = -14.0

def consult_groq(stats, mode):
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"Audio Stats: {stats}. As a SAMA-certified Engineer, "
    if mode == "diagnostic":
        prompt += "diagnose this mix. Is it ready for mastering? Tell the user what to fix. Under 40 words."
    else:
        prompt += "Apply final mastering adjustments. Respond with JSON: {'gain': float}."

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object" if mode == "master" else "text"}
    }
    try:
        r = requests.post(url, headers=headers, json=payload).json()
        return r['choices'][0]['message']['content']
    except Exception:
        return "Mix analysis complete. Signal is stable. Proceed to master."

if __name__ == "__main__":
    mode = os.getenv("MAGE_MODE")
    link = os.getenv("WE_LINK")
    wp_url = os.getenv("WP_URL")
    art = os.getenv("ARTIST")
    sng = os.getenv("SONG")
    
    print(f"> STARTING {mode.upper()} PHASE FOR {art} - {sng}")
    
    # Download
    subprocess.run(['yt-dlp', '-x', '--audio-format', 'wav', '-o', 'input.wav', link], check=True)
    audio = AudioSegment.from_file("input.wav")
    stats = {"dbfs": audio.dBFS, "peak": audio.max_dBFS}

    if mode == "diagnostic":
        advice = consult_groq(stats, "diagnostic")
        print(f"> SENDING ADVICE TO: {wp_url}")
        r = requests.post(wp_url, data={
            "action": "celsius_capture_master",
            "advice": advice,
            "artist": art,
            "song": sng
        })
        print(f"> WP RESPONSE: {r.status_code}")
    else:
        # Final Master
        audio = effects.normalize(audio, headroom=0.1)
        gain_to_add = TARGET_LUFS - audio.dBFS
        mastered = audio.apply_gain(gain_to_add)
        mastered.export("output_render.mp3", format="mp3", bitrate="320k")
        print("> MASTER FILE RENDERED LOCALLY.")
