import os
import requests
import sys
from pydub import AudioSegment

def download_file_from_google_drive(url, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    # Convert standard link to direct download link
    if 'drive.google.com' in url:
        if '/file/d/' in url:
            file_id = url.split('/file/d/')[1].split('/')[0]
        else:
            file_id = url.split('id=')[1].split('&')[0]
        
        direct_url = "https://docs.google.com/uc?export=download"
        session = requests.Session()
        response = session.get(direct_url, params={'id': file_id}, stream=True)
        token = get_confirm_token(response)

        if token:
            params = {'id': file_id, 'confirm': token}
            response = session.get(direct_url, params=params, stream=True)
        
        save_response_content(response, destination)
    else:
        # Standard download for non-Drive links
        response = requests.get(url, stream=True)
        save_response_content(response, destination)

def execute_signal_chain():
    we_link = os.getenv('WE_LINK')
    artist = os.getenv('ARTIST', 'Studio').replace(" ", "_")
    song = os.getenv('SONG', 'Master').replace(" ", "_")
    
    print(f"--- INGESTING SOURCE: {artist} // {song} ---")

    try:
        download_file_from_google_drive(we_link, "raw_input.wav")
        
        # Verify if the file is actually audio or just HTML error text
        with open("raw_input.wav", "rb") as f:
            header = f.read(4)
            if header != b'RIFF' and header != b'ID3\x03' and header != b'\xff\xfb':
                print(">>> ERROR: INGESTED DATA IS NOT A VALID AUDIO BITSTREAM.")
                print(">>> ENSURE GOOGLE DRIVE LINK IS SET TO 'ANYONE WITH THE LINK'.")
                sys.exit(1)

        print(">>> SOURCE SIGNAL VERIFIED.")

        # 2. DSP Mastering Chain
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
