import os, json, subprocess, requests
from pydub import AudioSegment, effects

# STANDARDS
TARGET_LUFS = -14.0
TRUE_PEAK_LIMIT = -1.0

def get_groq_analysis(audio_stats, mode="diagnostic"):
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    if mode == "diagnostic":
        prompt = f"Analyze these audio stats: {audio_stats}. Act as a Senior Sound Engineer. Tell the user if their mix is ready or what to fix (e.g., 'too much low end', 'clipping'). Keep it under 50 words. Ask if they want to proceed anyway."
    else:
        prompt = f"Provide final mastering gain for these stats: {audio_stats} to hit -14 LUFS. Return ONLY a JSON: {{'gain': float}}"

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object" if mode != "diagnostic" else "text"}
    }
    response = requests.post(url, headers=headers, json=payload).json()
    return response['choices'][0]['message']['content']

if __name__ == "__main__":
    mode = os.getenv("MAGE_MODE", "diagnostic")
    link = os.getenv("WE_LINK")
    
    # Download
    subprocess.run(['yt-dlp', '-x', '--audio-format', 'wav', '-o', 'input.wav', link], check=True)
    audio = AudioSegment.from_file("input.wav")
    stats = {"dbfs": audio.dBFS, "max_db": audio.max_dbfs}

    if mode == "diagnostic":
        advice = get_groq_analysis(stats, "diagnostic")
        # Post advice back to WP
        requests.post(os.getenv("WP_URL"), data={
            "action": "celsius_post_diagnostic",
            "advice": advice,
            "artist": os.getenv("ARTIST"),
            "song": os.getenv("SONG")
        })
    else:
        # Proceed with Mastering
        audio = effects.normalize(audio, headroom=0.1)
        audio = audio.apply_gain(TARGET_LUFS - audio.dBFS)
        audio.export("output_render.mp3", format="mp3", bitrate="320k")
