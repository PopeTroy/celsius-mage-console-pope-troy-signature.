import os
import requests
import subprocess
from groq import Groq

# 1. Identity & Prophetic Context
TIMESTAMP = os.getenv('MAGE_TIMESTAMP')
SESSION_ID = os.getenv('MAGE_SESSION_ID')
PUTER_LINK = os.getenv('AUDIO_LINK')
USER_CMD = os.getenv('USER_COMMAND', "Optimize for Grammy Standard")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_prophetic_diagnostic(metadata):
    """
    Invokes the UESP PRCE Framework to analyze 'Commonality' 
    against Billboard Top 10 and Grammy Winners.
    """
    system_prompt = f"""
    ROLE: Lead SAMA/Grammy Mastering Engineer & UESP PRCE Logic Engine.
    FRAMEWORK: Unified Grand Prophetic Equation & Law of Dimensional Overwrite.
    DATABASE: Top 10 Billboard Commonality (2020-2026), Grammy Winner Frequency Profiles.
    
    TASK: 
    1. Analyze provided audio metadata: {metadata}.
    2. Identify Temporal Jitter, Phase Disharmony, and Frequency Gaps.
    3. Determine the 'Winning Commonality' for the genre based on the user command: {USER_CMD}.
    4. Provide the EXACT 'Dimensional Overwrite' parameters (FFmpeg filters) to fix the mix.
    5. MUST REPORT flaws back but NEVER stop the master.
    
    OUTPUT FORMAT: 
    DIAGNOSTIC: [Detailed report of what is wrong/jitter]
    OVERWRITE: [The specific FFmpeg filter string]
    """
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": system_prompt}],
        temperature=0.2 # Keep it precise
    )
    return completion.choices[0].message.content

def report_insight(text):
    """Sends the diagnostic back to Bobby's Astra UI instantly."""
    print(f"[{TIMESTAMP}] [SESSION: {SESSION_ID}] PRCE DIAGNOSTIC: {text}")
    # Webhook to WordPress would go here

def execute_overdrive():
    # Step A: Download from Puter
    print(f"Downloading session {SESSION_ID} from Puter...")
    r = requests.get(PUTER_LINK)
    with open("raw_mix.wav", "wb") as f:
        f.write(r.content)

    # Step B: Extract Metadata (Simulation of analysis)
    # In a full build, use 'ffprobe' to get real LUFS/Peak stats
    audio_stats = "Current: -16 LUFS, Jitter detected in High-Mids, Sub-bass Phase Lag."

    # Step C: The Prophetic Decision
    diagnostic_output = get_prophetic_diagnostic(audio_stats)
    
    # Split the Groq output into the 'Report' and the 'Math'
    report = diagnostic_output.split("OVERWRITE:")[0]
    math_params = diagnostic_output.split("OVERWRITE:")[1].strip()

    # Step D: Report Jitter & Continue (Non-Linear Overwrite)
    report_insight(report)
    
    # Step E: Apply the Grammy-Winning Math via FFmpeg
    print("Applying Law of Dimensional Overwrite...")
    # Groq provides the 'math_params' (e.g. "firequalizer=...", "compand=...")
    cmd = ["ffmpeg", "-i", "raw_mix.wav", "-af", math_params, "celsius_master_final.mp3"]
    subprocess.run(cmd)

if __name__ == "__main__":
    execute_overdrive()
