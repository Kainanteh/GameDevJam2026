import wave
import struct
import subprocess
import os

def analyze_audio():
    mp3_path = "/home/kainanteh/game-dev-jam-2026/assets/Crux Noctis.mp3"
    wav_path = "/home/kainanteh/game-dev-jam-2026/scratch/temp_crux.wav"
    
    # 1. Convert MP3 to WAV using ffmpeg
    print("Converting MP3 to WAV...")
    subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-ac", "1", "-ar", "16000", wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if not os.path.exists(wav_path):
        print("Failed to convert file.")
        return
        
    # 2. Read the WAV file
    print("Analyzing amplitude envelope...")
    with wave.open(wav_path, "rb") as w:
        params = w.getparams()
        n_frames = w.getnframes()
        sample_rate = w.getframerate()
        
        # Read all frames as 16-bit integers
        frames = w.readframes(n_frames)
        data = struct.unpack(f"<{n_frames}h", frames)
        
    # Clean up temp WAV
    os.remove(wav_path)
    
    # Calculate RMS amplitude in 0.5 second windows (1 beat at 120 BPM)
    window_size = int(0.5 * sample_rate) # 8000 samples per half-second
    envelope = []
    
    for i in range(0, n_frames, window_size):
        chunk = data[i:i+window_size]
        if not chunk:
            break
        # Calculate RMS
        rms = (sum(x**2 for x in chunk) / len(chunk))**0.5
        envelope.append((i / sample_rate, rms))
        
    # Print amplitude of the last 40 seconds (80 beats)
    print("\n--- Last 40 seconds amplitude envelope (Time, RMS): ---")
    duration = n_frames / sample_rate
    last_40_start_idx = max(0, len(envelope) - 80)
    
    for idx in range(last_40_start_idx, len(envelope)):
        time_sec, rms = envelope[idx]
        print(f"Time: {time_sec:6.2f}s | RMS: {rms:8.2f} | " + "#" * int(rms / 100))

if __name__ == "__main__":
    analyze_audio()
