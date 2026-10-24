import sys
import os
import librosa
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

# Usage: python analyzer.py <audio file> [annotated boundary times in seconds]
# Example: python analyzer.py cue.wav 33 94 104 137

if len(sys.argv) < 2:
    print("Usage: python analyzer.py <audio file> [annotated boundary times]")
    sys.exit(1)

audio_path = sys.argv[1]
annotations = [float(t) for t in sys.argv[2:]]
name = os.path.splitext(os.path.basename(audio_path))[0]

# Settings
silence_threshold = 0.02   # mask brightness below 2% of max energy
novelty_window = 8         # seconds compared on each side of each moment
max_boundaries = 8         # number of strongest novelty peaks reported
tolerance = 3              # seconds, standard MIR boundary tolerance

def standardize(v):
    return (v - v.mean()) / (v.std() + 1e-8)

# Load
y, sr = librosa.load(audio_path)
duration = librosa.get_duration(y=y, sr=sr)

# Energy
rms = librosa.feature.rms(y=y)[0]
times = librosa.times_like(rms, sr=sr)

# Brightness
centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
centroid[rms < rms.max() * silence_threshold] = np.nan

# Tempo and beats
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
bpm = float(np.atleast_1d(tempo)[0])
beat_times = librosa.frames_to_time(beats, sr=sr)

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

# Meter
meter_text = "not enough beats"
meter_scores = {}
if len(beats) >= 8:
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    beat_onset = onset_env[beats]
    beat_chroma = librosa.util.sync(chroma, beats, aggregate=np.median)[:, 1:]
    chroma_change = np.linalg.norm(np.diff(beat_chroma, axis=1), axis=0)
    chroma_change = np.concatenate([[0], chroma_change])
    accent = standardize(beat_onset) + standardize(chroma_change)
    for m in [3, 4]:
        meter_scores[m] = max(accent[p::m].mean() for p in range(m))
    meter = max(meter_scores, key=meter_scores.get)
    meter_text = f"{meter} beats per bar"

# Structure features: harmony (chroma) + timbre (MFCC)
mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
n = min(chroma.shape[1], mfcc.shape[1])
features = np.vstack([chroma[:, :n], mfcc[:, :n]])
features = (features - features.mean(axis=1, keepdims=True)) / (features.std(axis=1, keepdims=True) + 1e-8)

# Novelty-based boundaries
win = int(novelty_window * sr / 512)
cs = np.cumsum(np.pad(features, ((0, 0), (1, 0))), axis=1)
t_idx = np.arange(win, n - win)
novelty = np.zeros(n)
if len(t_idx):
    before = (cs[:, t_idx] - cs[:, t_idx - win]) / win
    after = (cs[:, t_idx + win] - cs[:, t_idx]) / win
    novelty[t_idx] = np.linalg.norm(after - before, axis=0)

peaks, props = find_peaks(novelty, distance=win, prominence=0)
top = np.argsort(props["prominences"])[::-1][:max_boundaries]
top_frames = np.sort(peaks[top])
peak_times = librosa.frames_to_time(top_frames, sr=sr)

# Report
lines = [
    f"File: {audio_path}",
    f"Duration: {duration:.1f} s",
    f"Tempo: {bpm:.1f} BPM ({len(beat_times)} beats detected), half/double: {bpm/2:.1f} / {bpm*2:.1f}",
    f"Meter: {meter_text}",
    f"Meter scores: " + ", ".join(f"{k}: {v:.2f}" for k, v in meter_scores.items()),
    f"Key: {best_key} (confidence {best_score:.2f})",
    "Detected boundaries (s): " + ", ".join(f"{t:.1f}" for t in peak_times),
]

if annotations:
    hits = 0
    lines.append(f"Annotated vs detected ({tolerance}s tolerance):")
    for a in annotations:
        if len(peak_times) == 0:
            lines.append(f"  {a:.1f} -> nothing detected, miss")
            continue
        nearest = peak_times[np.argmin(np.abs(peak_times - a))]
        diff = nearest - a
        hit = abs(diff) <= tolerance
        hits += hit
        lines.append(f"  {a:.1f} -> {nearest:.1f} ({diff:+.1f}s) {'hit' if hit else 'miss'}")
    lines.append(f"Found {hits} of {len(annotations)}")

report = "\n".join(lines)
print(report)
with open(f"{name}_report.txt", "w") as f:
    f.write(report + "\n")

# Plot
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
fig.suptitle(f"{name}   |   Tempo: {bpm:.1f} BPM   |   Meter: {meter_text}   |   Key: {best_key}   |   {duration:.1f}s", fontsize=13)

ax1.plot(times, rms)
if len(beat_times):
    ax1.vlines(beat_times, 0, rms.max(), color="red", alpha=0.2)
ax1.set_title("Energy with detected beats")
ax1.set_ylabel("RMS")

ax2.plot(times, centroid, color="orange")
ax2.set_title("Brightness (spectral centroid)")
ax2.set_ylabel("Hz")

novelty_times = librosa.times_like(novelty, sr=sr)
ax3.plot(novelty_times, novelty, color="purple")
ax3.plot(peak_times, novelty[top_frames], "o", color="red")
for t in annotations:
    ax3.axvline(t, color="green", linestyle=":")
ax3.set_title(f"Novelty ({novelty_window}s window): red = detected, green = annotated")
ax3.set_ylabel("Change")
ax3.set_xlabel("Time (seconds)")

for t in peak_times:
    ax1.axvline(t, color="black", linestyle="--", alpha=0.6)
    ax2.axvline(t, color="black", linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig(f"{name}_analysis.png", dpi=150)
plt.close()
print(f"Saved {name}_analysis.png and {name}_report.txt")