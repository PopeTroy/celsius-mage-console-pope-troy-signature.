import sys
import os
import matchering as mg
import ffmpeg
from groq import Groq

# Capture WordPress Data
# Order: Artist, Song, Instruments, Goals, SongURL, RefURL
try:
    artist, song, instruments, goals, song_url, ref_url = sys.argv[1:7]
except ValueError:
    print("Error: Missing arguments from WordPress dispatch.")
    sys.exit(1)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_sonic_dna():
    print("> QUERYING GROQ SOVEREIGN DATABASE...")
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are the PRCE Acoustic Intelligence. Provide precise mastering offsets (EQ/Compression) in text format."},
            {"role": "user", "content": f"Instruments: {instruments}. Goals: {goals}"}
        ]
    )
    return completion.choices[0].message.content

def run_master():
    print(f"> STARTING UESP PRCE: {song.upper()} by {artist.upper()}")
    
    # Download input file
    os.system(f"curl -L '{song_url}' -o input_track.wav")
    
    # Determine Reference
    ref = "database/award_winner.wav" # Ensure this file exists in your repo
    if ref_url and ref_url != "undefined" and ref_url != "":
        os.system(f"curl -L '{ref_url}' -o ref.wav")
        ref = "ref.wav"

    # Mastering Process
    dna = get_sonic_dna()
    mg.process(target="input_track.wav", reference=ref, results=[mg.Result("temp.wav", subtype="pcm_24")])

    # Burn Metadata & Royalty Info
    final_output = f"{song.replace(' ', '_')}_WINNER.wav"
    (
        ffmpeg
        .input("temp.wav")
        .output(final_output, **{
            'metadata': f'artist={artist}',
            'metadata': f'title={song}',
            'metadata': 'copyright=Celsius Technology & Media Group',
            'metadata': f'comment=Royalty Agreement: 30% Thabelo Moahi (ASCAP). UESP PRCE DNA: {dna[:100]}',
        })
        .run(overwrite_output=True)
    )
    print("> GREEN CHECK: MASTERING SUCCESSFUL")

if __name__ == "__main__":
    run_master()
