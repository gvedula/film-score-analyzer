import librosa
import matplotlib.pyplot as plt
import numpy as np

# Load
y, sr = librosa.load("cue.wav")
duration = librosa.get_duration(y=y, sr=sr)
print("Sample rate:", sr)
print("Duration in seconds:", round(duration, 2))

# Energy
rms = librosa.feature.rms(y=y)[0]
times = librosa.times_like(rms, sr=sr)
# Brightness
centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
centroid[rms < rms.max() * 0.02] = np.nan

# Tempo and beats
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
bpm = float(np.atleast_1d(tempo)[0])
beat_times = librosa.frames_to_time(beats, sr=sr)
print("Estimated tempo:", round(bpm, 1), "BPM")
print("Beats detected:", len(beat_times))

# Key and mode
chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
chroma_avg = chroma.mean(axis=1)

notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

best_score = -1
best_key = None

for i in range(12):
    major_score = np.corrcoef(chroma_avg, np.roll(major_profile, i))[0, 1]
    minor_score = np.corrcoef(chroma_avg, np.roll(minor_profile, i))[0, 1]
    if major_score > best_score:
        best_score = major_score
        best_key = notes[i] + " major"
    if minor_score > best_score:
        best_score = minor_score
        best_key = notes[i] + " minor"

print("Estimated key:", best_key)
print("Confidence:", round(best_score, 2))

# Plot (always last)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
fig.suptitle(f"Tempo: {round(bpm, 1)} BPM   |   Key: {best_key}   |   Duration: {round(duration, 1)}s", fontsize=13)

ax1.plot(times, rms)
ax1.vlines(beat_times, 0, rms.max(), color="red", alpha=0.2)
ax1.set_title("Energy Envelope with Detected Beats")
ax1.set_ylabel("Energy (RMS)")

ax2.plot(times, centroid, color="orange")
ax2.set_title("Brightness (Spectral Centroid)")
ax2.set_ylabel("Hz")
ax2.set_xlabel("Time (seconds)")

plt.tight_layout()
plt.savefig("analysis.png")
plt.show()