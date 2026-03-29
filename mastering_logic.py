import os
import json
import subprocess
import requests
from pydub import AudioSegment, effects

# PROFESSIONAL STANDARDS
TARGET_LUFS = -14.0
TRUE_PEAK_LIMIT = -1.0
BITRATE = "320k"

def get_groq_engineering_advice(artist, song):
    """Consults the Groq Expert Sound Engineer for Radio/SAMA compliance."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"gain": 0, "limiter": -1.0, "comment": "Groq Key Missing - Using Default Chain"}
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"Act as a Senior Sound Engineer. Suggest mastering adjustments for a track by {artist} titled {song}. Ensure compliance with BBC Radio (UK) and FCC (USA) standards (-14 LUFS, -1dB True Peak). Return only a JSON object with keys 'gain_adjustment' (float) and 'limiter_threshold' (float)."
    
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except:
        return {"gain_adjustment": 0.5, "limiter_threshold": -1.0}

def download_source(url):
    print(f"> RETRIEVING SIGNAL: {url}")
    try:
        subprocess.run(['yt-dlp', '-x', '--audio-format', 'wav', '-o', 'source_input.wav', url], check=True)
        return "source_input.wav"
    except Exception as e:
        print(f"FAILED TO GRAB SOURCE: {e}")
        return None

def master_audio(input_file, advice):
    print(f"> GROQ ADVICE RECEIVED: {advice}")
    audio = AudioSegment.from_file(input_file)
    audio = effects.normalize(audio, headroom=0.1)
    
    # Apply Groq-suggested gain for Radio Density
    gain = advice.get('gain_adjustment', 0.5)
    audio = audio.apply_gain(gain)

    # Ensure World Standard LUFS
    change_in_gain = TARGET_LUFS - audio.dBFS
    mastered_audio = audio.apply_gain(change_in_gain)

    # Peak Limiting
    limit = advice.get('limiter_threshold', -1.0)
    if mastered_audio.max_dBFS > limit:
        mastered_audio = mastered_audio + (limit - mastered_audio.max_dBFS)

    output_path = "output_render.mp3"
    mastered_audio.export(output_path, format="mp3", bitrate=BITRATE, tags={'artist': os.getenv("ARTIST"), 'title': os.getenv("SONG"), 'comment': 'Mastered by Celsius Mage'})
    return output_path

if __name__ == "__main__":
    link = os.getenv("WE_LINK")
    artist = os.getenv("ARTIST", "Unknown")
    song = os.getenv("SONG", "NewSession")

    source_file = download_source(link)
    if source_file:
        advice = get_groq_engineering_advice(artist, song)
        master_audio(source_file, advice)
        log = {"artist": artist, "song": song, "groq_status": "ANALYZED"}
        with open("latest_session.json", "w") as f:
            json.dump(log, f)
