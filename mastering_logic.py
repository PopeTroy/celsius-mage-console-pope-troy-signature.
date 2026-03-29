import os, json, subprocess, requests
from pydub import AudioSegment, effects

TARGET_LUFS = -14.0

if __name__ == "__main__":
    mode = os.getenv("MAGE_MODE", "diagnostic")
    link = os.getenv("WE_LINK")
    session_id = os.getenv("SESSION_ID", "default_session")
    wp_url = "https://celsiusmediagroup.co.za/wp-json/celsius/v1/mage"
    
    # Download
    subprocess.run(['yt-dlp', '-x', '--audio-format', 'wav', '-o', 'input.wav', link], check=True)
    audio = AudioSegment.from_file("input.wav")
    stats = {"dbfs": round(audio.dBFS, 2), "peak": round(audio.max_dBFS, 2)}

    if mode == "diagnostic":
        # Simplified Engine Advice
        advice = f"Analysis Complete: Mix sitting at {stats['dbfs']}dBFS. Peak at {stats['peak']}dB. Logic suggests PRCE V12 Mastering is safe to engage."
        requests.post(wp_url, data={"advice": advice, "session_id": session_id})
    else:
        # Master
        audio = effects.normalize(audio, headroom=0.1)
        mastered = audio.apply_gain(TARGET_LUFS - audio.dBFS)
        mastered.export("render.mp3", format="mp3", bitrate="320k")
        with open("render.mp3", "rb") as f:
            requests.post(wp_url, files={"master_file": f}, data={"session_id": session_id})
