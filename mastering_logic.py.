import sys
import os
import matchering as mg
import ffmpeg

# Receiving data from your WordPress Page
artist = sys.argv[1]
song = sys.argv[2]
instruments = sys.argv[3]
goals = sys.argv[4]

def run_celsius_protocol():
    print(f"--- ACTIVATING UESP PRCE FOR {artist.upper()} ---")
    
    # 1. High-Fidelity Synthesis
    # Using the 'award_winner.wav' from your GitHub database
    mg.process(
        target="input_track.wav",
        reference="database/award_winner.wav",
        results=[mg.Result("winner_render.wav", subtype="pcm_24")]
    )

    # 2. Burn Metadata & 30% ASCAP Royalty
    (
        ffmpeg
        .input("winner_render.wav")
        .output(f"{song}_CELSIUS_MASTER.wav", **{
            'metadata': f'artist={artist}',
            'metadata': f'title={song}',
            'metadata': 'copyright=Celsius Technology & Media Group',
            'metadata': f'comment=Royalty: 30% Thabelo Moahi (ASCAP). Goals: {goals}',
        })
        .run(overwrite_output=True)
    )
    print("> GREEN CHECK: MASTERING COMPLETE")

if __name__ == "__main__":
    run_celsius_protocol()
import os
from groq import Groq

# Initialize Groq with your Sovereign Database Key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_groq_sonic_dna(instruments, goals):
    print("> QUERYING SOVEREIGN DATABASE (GROQ)...")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are the PRCE Acoustic Intelligence. Provide precise EQ curves (Hz/dB) and compression settings for mastering."
            },
            {
                "role": "user",
                "content": f"Analyze these elements: {instruments}. Goal: {goals}. Provide a mastering profile."
            }
        ],
        model="llama3-70b-8192", # Using the heavy-duty LPU model
    )
    return chat_completion.choices[0].message.content

# This replaces the need for 'award_winner.wav' if it's missing
