import os, json, subprocess, requests, base64
from pydub import AudioSegment, effects

TARGET_LUFS = -14.0

if __name__ == "__main__":
    mode = os.getenv("MAGE_MODE", "diagnostic")
    link = os.getenv("WE_LINK")
    session_id = os.getenv("SESSION_ID")
    
    # AUTHENTICATION - BOBBY
    wp_user = "Bobby" 
    wp_app_pass = os.getenv("WP_APP_PASS")
    
    # Create Base64 Encoded Header (More reliable than BasicAuth for some servers)
    user_pass = f"{wp_user}:{wp_app_pass}"
    encoded_u = base64.b64encode(user_pass.encode()).decode()
    headers = {"Authorization": f"Basic {encoded_u}"}
    
    wp_url = "https://celsiusmediagroup.co.za/wp-json/celsius/v1/mage"
    
    # 1. Download & Analyze
    subprocess.run(['yt-dlp', '-x', '--audio-format', 'wav', '-o', 'input.wav', link], check=True)
    audio = AudioSegment.from_file("input.wav")
    stats = {"dbfs": round(audio.dBFS, 2), "peak": round(audio.max_dBFS, 2)}

    if mode == "diagnostic":
        # Simplified for testing
        advice = f"Mix analyzed at {stats['dbfs']}dBFS. Peak at {stats['peak']}dB."
        data = {"advice": advice, "status": "READY", "session_id": session_id}
        r = requests.post(wp_url, headers=headers, data=data)
        print(f"WP Handshake: {r.status_code} - {r.text}")
    else:
        audio = effects.normalize(audio, headroom=0.1)
        mastered = audio.apply_gain(TARGET_LUFS - audio.dBFS)
        mastered.export("render.mp3", format="mp3", bitrate="320k")
        with open("render.mp3", "rb") as f:
            r = requests.post(wp_url, headers=headers, files={"master_file": f}, data={"session_id": session_id})
        print(f"WP Upload: {r.status_code} - {r.text}")
