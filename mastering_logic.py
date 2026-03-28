import sys
import os
import matchering as mg
import ffmpeg
from groq import Groq

# Order: script, artist, song, instruments, goals, song_url
artist, song, instruments, goals, song_url = sys.argv[1:6]

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_acoustic_intelligence():
    print("> CALLING LLAMA 3.3 ACOUSTIC LAYER...")
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile", # Latest Llama 3.3 Version
        messages=[
            {"role": "system", "content": "You are the PRCE Acoustic Intelligence. Return only numeric EQ and compression specs."},
            {"role": "user", "content": f"Instruments: {instruments}. Goals: {goals}"}
        ]
    )
    return completion.choices[0].message.content

def process_master():
    print(f"> RENDER INITIATED: {song} by {artist}")
    os.system(f"curl -L '{song_url}' -o input.wav")
    
    dna = get_acoustic_intelligence()
    
    # Mastering Logic
    mg.process(target="input.wav", reference="database/award_winner.wav", results=[mg.Result("temp.wav", subtype="pcm_24")])

    # Metadata & 30% Royalty for Thabelo Moahi (ASCAP)
    final_file = f"{song.replace(' ', '_')}_WINNER.wav"
    (
        ffmpeg.input("temp.wav")
        .output(final_file, **{
            'metadata': f'artist={artist}',
            'metadata': f'title={song}',
            'metadata': 'copyright=Celsius Technology & Media Group',
            'metadata': f'comment=Royalty: 30% Thabelo Moahi (ASCAP). DNA: {dna[:50]}',
        }).run(overwrite_output=True)
    )
    print("> GREEN CHECK: SUCCESS")

if __name__ == "__main__":
    process_master()
