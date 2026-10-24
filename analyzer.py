import librosa
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

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
# Segmentation
mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
n = min(chroma.shape[1], mfcc.shape[1])
features = np.vstack([chroma[:, :n], mfcc[:, :n]])
features = (features - features.mean(axis=1, keepdims=True)) / (features.std(axis=1, keepdims=True) + 1e-8)

bounds = librosa.segment.agglomerative(features, 5)
bound_times = librosa.frames_to_time(bounds, sr=sr)
print("Section boundaries (s):", [round(float(t), 1) for t in bound_times])

# Novelty-based boundaries
win = int(8 * sr / 512)
n_frames = features.shape[1]
cs = np.cumsum(np.pad(features, ((0, 0), (1, 0))), axis=1)
t_idx = np.arange(win, n_frames - win)
before = (cs[:, t_idx] - cs[:, t_idx - win]) / win
after = (cs[:, t_idx + win] - cs[:, t_idx]) / win
novelty = np.zeros(n_frames)
novelty[t_idx] = np.linalg.norm(after - before, axis=0)

peaks, props = find_peaks(novelty, distance=win, prominence=0)
strengths = props["prominences"]
top = np.argsort(strengths)[::-1][:8]

print("Top novelty peaks (time in s, strength):")
for i in sorted(top, key=lambda i: peaks[i]):
    print(round(float(librosa.frames_to_time(peaks[i], sr=sr)), 1), round(float(strengths[i]), 2))

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
# Meter
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
beat_onset = onset_env[beats]

beat_chroma = librosa.util.sync(chroma, beats, aggregate=np.median)[:, 1:]
chroma_change = np.linalg.norm(np.diff(beat_chroma, axis=1), axis=0)
chroma_change = np.concatenate([[0], chroma_change])

def standardize(v):
    return (v - v.mean()) / (v.std() + 1e-8)

accent = standardize(beat_onset) + standardize(chroma_change)

meter_scores = {}
for m in [3, 4]:
    meter_scores[m] = max(accent[p::m].mean() for p in range(m))

meter = max(meter_scores, key=meter_scores.get)
print("Estimated meter:", meter, "beats per bar")
print("Meter scores:", {k: round(float(v), 2) for k, v in meter_scores.items()})

# Plot (always last)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
fig.suptitle(f"Tempo: {round(bpm, 1)} BPM   |   Meter: {meter} beats per bar   |   Key: {best_key}   |   Duration: {round(duration, 1)}s", fontsize=13)

ax1.plot(times, rms)
ax1.vlines(beat_times, 0, rms.max(), color="red", alpha=0.2)
ax1.set_title("Energy Envelope with Detected Beats")
ax1.set_ylabel("Energy (RMS)")

ax2.plot(times, centroid, color="orange")
ax2.set_title("Brightness (Spectral Centroid)")
ax2.set_ylabel("Hz")
novelty_times = librosa.times_like(novelty, sr=sr)
ax3.plot(novelty_times, novelty, color="purple")
ax3.plot(librosa.frames_to_time(peaks[top], sr=sr), novelty[peaks[top]], "o", color="red")
for t in [33, 94, 104, 137]:
    ax3.axvline(t, color="green", linestyle=":")
ax3.set_title("Novelty (8s window): red = top peaks, green = your annotated boundaries")
ax3.set_ylabel("Change")
ax3.set_xlabel("Time (seconds)")
for t in bound_times:
    ax1.axvline(t, color="black", linestyle="--")
    ax2.axvline(t, color="black", linestyle="--")

plt.tight_layout()
plt.savefig("analysis.png")
plt.show()