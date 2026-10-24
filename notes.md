# Validation notes: Film Score Analyzer

## Annotation rule (applies to all cues)
- A boundary is the start of a new formal section: new material,
  texture, or function lasting at least a few bars
- The start of a repeated section counts (A then A is two sections)
- Single entrances or short gestures inside a section do not count
- Transitions are marked where the new section lands, not where
  the build starts
- All answer keys come from the DAW session, not memory
- Rule written after the first runs. Original answer keys are kept
  below for comparison

## Scorecard (novelty, 8s window, 3s tolerance, revised keys)
- Cue 1: 2 of 3 (33, 137)
- Cue 2: 3 of 5 (11, 25, 48)
- Total: 5 of 8

---

# Cue 1 (D minor, 90 BPM, 4/4, ~3:02)

## Energy
- Opening hits at ~3s and ~13s, full entrance at ~33s, dense middle,
  drop at ~137s, tail fades out by ~172s
- Matches the actual build and release structure of the cue

## Tempo
- Detected 89.1 BPM vs actual 90 BPM, 201 beats detected
- Difference is frame resolution, not error: hop of 512 samples at
  22050 Hz is ~23 ms per frame. Beat spacing of 29 frames = 89.1 BPM,
  28 frames = 92.3 BPM. 90 falls between, so 89.1 is the closest possible
- Beat tracking stops at ~137s where the cue drops into the tail
- Tail after ~137s has no pulse (confirmed). The tracker correctly
  stopped detecting beats where the meter ends

## Key
- Detected D minor, correct
- Confidence 0.64 (Krumhansl-Kessler profile matching on averaged chroma)

## Brightness
- Unmasked version showed a 5600 Hz spike at ~2.8s on the opening synth hit
- That reading came from a frame that was mostly silence with only the
  first sliver of the attack: tiny sharp transient + near silence =
  very high centroid, very low energy. Measuring the onset click,
  not the sound of the hit
- Masked brightness wherever RMS < 2% of max. Removes silence before
  the hit and the faded tail after ~172s
- Once sounding, the hit sits around 1000 Hz
- Brightness climbs from 100 to 137s while energy stays roughly level,
  matches the brighter orchestration in that section (confirmed)
- Tradeoff: higher threshold removes more noise but can hide quiet
  passages; 2% removed silence without touching any validated passage

## Meter
- Detected 4 beats per bar, correct
- Scores: 3 = 0.06, 4 = 0.42. Clear separation, high confidence
- Method: accent per beat = onset strength + harmonic change,
  tested which grouping makes downbeats stand out most
- Only tests 3 vs 4. Can't separate 2 from 4, and can't determine
  the bottom number of the time signature from audio

## Original answer key (before the rule)
- 33: main section lands
- 94: low strings enter
- 104: beat drop
- 137: tail begins, no pulse
- Memory originally said the main section started at 29; the session
  says 33. Answer keys have to come from the session

## Revised answer key (rule applied)
- 33, 94, 137. 104 treated as the peak of the section that starts
  at 94, not a new section
- Result: 2 of 3 (33, 137). Same detections as before, only the
  key changed
- Miss at 94: nearest peak 87.7 is a phrase turnover, not the
  string entrance

## Segmentation, agglomerative (k=5, chroma + MFCC), since removed
- Boundaries: 0.0, 33.6, 98.7, 140.4, 174.7
- Hit: 33 vs 33.6
- Transition 94 (low strings) to 104 (beat drop): one boundary at
  98.7, halfway between. Clustering splits gradual transitions down
  the middle and misses both edges
- Near miss: 137 vs 140.4, just outside the standard 3s window
- Split off the fade at 174.7 as its own section; did not split off
  the silence before the opening hit
- Had to be told the number of sections. Replaced by novelty
  detection, which doesn't need it

## Novelty detection, 4s window
- Missed all section boundaries
- Found peaks at 55.2, 65.9, 76.5, 87.2, ~10.7s apart
- 4 bars at 89.1 BPM = 10.8s. Confirmed something changes every
  4 bars in the main section. Detected phrase structure, not sections

## Novelty detection, 8s window (current setting)
- Peaks: 19.6, 30.8, 45.3, 55.9, 66.0, 76.9, 87.7, 139.6
- Hit: 33 vs 30.8 (weak peak)
- Hit: 137 vs 139.6, the strongest peak in the cue
- 94 missed. Only a weak bump near 97, close to where agglomerative
  put its boundary (98.7). Two methods agree the features see one
  mild change there, not two events
- 4 bar phrase peaks persisted at both window sizes
- 104 to 137 has the lowest novelty in the cue: the climax is the
  most internally consistent section
- First and last 8s are blind spots, the window can't extend past
  the edges of the file
- Likely cause of the weak response near 94 to 104: the beat drop
  is a rhythmic change, and averaged chroma + MFCC can't see rhythm

---

# Cue 2 (C major, 60 BPM, 4/4, ~61s)

## Tempo and meter
- Tempo: 123 BPM, doubled from 60. Classic octave error. 123 is the
  nearest frame resolution step to 120
- Meter: 4 beats per bar, correct label, but counting at double
  speed, so "4 beats" is really 2 real beats. Tempo error carries
  into meter

## Key
- C major, correct, confidence 0.88 (higher than cue 1). One D major
  chord (secondary dominant) didn't affect the estimate

## Original answer key (before the rule)
- 4, 11, 17, 37, 48 (11 added after the first run, confirmed in
  session). Result: 2 of 5
- 4 was a 3 note flute gesture

## Revised answer key (rule applied)
- 11, 17, 25, 37, 48. Flute at 4 dropped, it's a short gesture
  inside a section. Repeat at 25 added under the rule, confirmed
  in session
- Result: 3 of 5 (11, 25, 48)
- 17 missed: only 6s after 11, closer than the 8s minimum spacing
  between detected boundaries, so only one of the two can be found
- 37 near miss at 33.6 (-3.4s), just outside the 3s window
- The tool detected the repeat at 24.8 before it was in the key

---

# Findings across cues
- Tempo is reliable at moderate tempos, doubles slow ones
- Key estimation correct on both, more confident on diatonic material
- Novelty detection hears phrases with short windows and sections
  with longer ones
- A fixed 8s window is too coarse for short cues with quick section
  changes. Window should scale with the cue
- Every parameter (2% threshold, 8s window) was first tuned on cue 1

# Ideas for later
- Add a rhythm feature so rhythmic changes like beat drops register
- Scale the novelty window to cue length or tempo
- Detect which sections are rhythmically driven vs free
- Smaller hop length for finer tempo resolution
- Correct tempo octave errors using a prior on film tempos
---

# Cue 3 (B♭ major, 80 BPM, 4/4, ~82s, tabla driven)

## Tempo and meter
- Tempo: 107.7 BPM vs actual 80. Ratio of roughly 4:3, not the usual
  2:1 octave error. Cue is built on an Indian tabla pattern with dense
  triplet subdivisions. The tracker locked onto a grouping within the
  subdivisions instead of the 80 BPM pulse
- Only 69 beats detected in 82s, so tracking dropped out for long
  stretches where the pattern was dense or syncopated
- Meter reported 4 beats per bar, matching 4/4, but it's measured on
  the wrong pulse, so the match is not meaningful
- Takeaway: librosa's beat tracker assumes Western pulse conventions
  and fails on tabla rhythm. A clear limitation for non-Western music

## Key
- Reported A# major = B♭ major, correct. Confidence 0.93, highest of
  the three cues. Label uses sharps because the code's note list does

## Boundaries
- Answer key: 6, 25, 36, 68
- Result: 4 of 4. 25 (+0.1), 36 (-1.3), 68 (+0.3)
- 6 matched at 8.0, the earliest frame the 8s window can detect.
  Counted as a hit, but the tool couldn't have placed it earlier
- Extra detections not in the key: 16.6, 48.0, 57.7 [fill in: repeats,
  phrase turnovers, or nothing?]