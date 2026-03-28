import sys
import os
import matchering as mg
import ffmpeg
from groq import Groq

# 1. Capture WordPress Data
artist, song, instruments, goals, song_url, ref_url = sys.argv[1:7]
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_sonic_dna():
    # Use Groq to determine the perfect mastering curve if no reference exists
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "system", "content": "Return only numerical EQ offsets and compression ratios for mastering based on user goals."},
                  {"role": "user", "content": f"Instruments: {instruments}. Goals: {goals}"}]
    )
    return completion.choices[0].message.content

def run_master():
    print(f"> STARTING UESP PRCE FOR {artist}...")
    
    # Download the track from WordPress URL (Simplified for script)
    os.system(f"curl -L {song_url} -o input_track.wav")
    
    # Use Groq logic to "Prophetically" master
    dna = get_sonic_dna()
    print(f"> GROQ ANALYSIS COMPLETE: {dna[:50]}...")

    # Execute Mastering
    # (Matches against internal 'database/award_winner.wav' or the user's ref_url)
    ref = "database/award_winner.wav" if not ref_url or ref_url == "undefined" else "ref.wav"
    if ref == "ref.wav": os.system(f"curl -L {ref_url} -o ref.wav")

    mg.process(target="input_track.wav", reference=ref, results=[mg.Result("temp.wav", subtype="pcm_24")])

    # Final Burn: Metadata & 30% Royalty for Thabelo Moahi
    (
        ffmpeg
        .input("temp.wav")
        .output(f"{song}_WINNER.wav", **{
            'metadata': f'artist={artist}',
            'metadata': f'title={song}',
            'metadata': 'copyright=Celsius Technology & Media Group',
            'metadata': f'comment=Royalty: 30% Thabelo Moahi (ASCAP). DNA: {dna[:100]}',
        })
        .run(overwrite_output=True)
    )
    print("> GREEN CHECK: UESP PRCE SUCCESSFUL")

if __name__ == "__main__":
    run_master()
