import os
import requests
import sys
from pydub import AudioSegment

def download_asset(url, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_content(response, destination):
        with open(destination, "wb") as f:
            for chunk in response.iter_content(32768):
                if chunk: f.write(chunk)

    if 'drive.google.com' in url:
        file_id = url.split('/file/d/')[1].split('/')[0] if '/file/d/' in url else url.split('id=')[1].split('&')[0]
        direct_url = "https://docs.google.com/uc?export=download"
        session = requests.Session()
        response = session.get(direct_url, params={'id': file_id}, stream=True)
        token = get_confirm_token(response)
        if token:
            response = session.get(direct_url, params={'id': file_id, 'confirm': token}, stream=True)
        save_content(response, destination)
    else:
        response = requests.get(url, stream=True)
        save_content(response, destination)

def execute_signal_chain():
    we_link = os.getenv('WE_LINK')
    artist = os.getenv('ARTIST', 'Studio').replace(" ", "_")
    song = os.getenv('SONG', 'Master').replace(" ", "_")
    
    print(f"--- INGESTING SOURCE: {artist} // {song} ---")

    try:
        download_asset(we_link, "raw_input.wav")
        
        # Verify Bitstream Integrity
        with open("raw_input.wav", "rb") as f:
            header = f.read(4)
            if header not in [b'RIFF', b'ID3\x03', b'\xff\xfb']:
                print(">>> ERROR: INVALID AUDIO BITSTREAM (LINK MAY BE PRIVATE).")
                sys.exit(1)

        print(">>> SOURCE SIGNAL VERIFIED.")

        # DSP Mastering Chain
        audio = AudioSegment.from_file("raw_input.wav")
        mastered = audio.normalize(headroom=0.1) 
        
        output_file = "output_render.mp3"
        mastered.export(output_file, format="mp3", bitrate="320k", parameters=["-ar", "48000"])
        
        print(f">>> RENDER COMPLETE: {output_file}")
            
    except Exception as e:
        print(f">>> SIGNAL FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    execute_signal_chain()
