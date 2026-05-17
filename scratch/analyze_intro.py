import wave
import struct
import subprocess
import os

def analyze_intro():
    mp3_path = "/home/kainanteh/game-dev-jam-2026/assets/Crux Noctis.mp3"
    wav_path = "/home/kainanteh/game-dev-jam-2026/scratch/temp_intro.wav"
    
    # Convert first 40 seconds of MP3 to WAV
    print("Converting first 40s of MP3 to WAV...")
    subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-t", "40", "-ac", "1", "-ar", "16000", wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if not os.path.exists(wav_path):
        print("Failed to convert file.")
        return
        
    with wave.open(wav_path, "rb") as w:
        n_frames = w.getnframes()
        sample_rate = w.getframerate()
        frames = w.readframes(n_frames)
        data = struct.unpack(f"<{n_frames}h", frames)
        
    os.remove(wav_path)
    
    # Calculate RMS in 0.5s windows
    window_size = int(0.5 * sample_rate)
    envelope = []
    
    for i in range(0, n_frames, window_size):
        chunk = data[i:i+window_size]
        if not chunk:
            break
        rms = (sum(x**2 for x in chunk) / len(chunk))**0.5
        envelope.append((i / sample_rate, rms))
        
    print("\n--- First 40 seconds amplitude envelope: ---")
    for time_sec, rms in envelope:
        print(f"Time: {time_sec:6.2f}s | RMS: {rms:8.2f} | " + "#" * int(rms / 100))

if __name__ == "__main__":
    analyze_intro()
