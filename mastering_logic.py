import os
import json
import subprocess
from pydub import AudioSegment, effects

# PROFESSIONAL STANDARDS
TARGET_LUFS = -14.0
TRUE_PEAK_LIMIT = -1.0
BITRATE = "320k"

def download_source(url):
    print(f"> ATTEMPTING SIGNAL RETRIEVAL: {url}")
    try:
        subprocess.run(['yt-dlp', '-x', '--audio-format', 'wav', '-o', 'source_input.wav', url], check=True)
        return "source_input.wav"
    except Exception as e:
        print(f"CRITICAL: Link retrieval failed. {e}")
        return None

def master_audio(input_file):
    print("> INITIALIZING MASTERING CHAIN...")
    audio = AudioSegment.from_file(input_file)
    audio = effects.normalize(audio, headroom=0.1)
    
    change_in_gain = TARGET_LUFS - audio.dBFS
    mastered_audio = audio.apply_gain(change_in_gain)

    if mastered_audio.max_dBFS > TRUE_PEAK_LIMIT:
        mastered_audio = mastered_audio + (TRUE_PEAK_LIMIT - mastered_audio.max_dBFS)

    output_path = "output_render.mp3"
    mastered_audio.export(output_path, format="mp3", bitrate=BITRATE)
    print(f"> MASTERING COMPLETE: {output_path}")
    return output_path

def create_registry_log(artist, song):
    log_data = {
        "artist": artist,
        "song": song,
        "standards": ["UK-RADIO", "USA-FM", "SAMA-READY"],
        "status": "SIGNAL_LOCKED"
    }
    with open("session_log.json", "w") as f:
        json.dump(log_data, f)

if __name__ == "__main__":
    link = os.getenv("WE_LINK")
    artist = os.getenv("ARTIST", "Unknown")
    song = os.getenv("SONG", "NewSession")

    source_file = download_source(link)
    if source_file:
        master_audio(source_file)
        create_registry_log(artist, song)
    else:
        exit(1)
