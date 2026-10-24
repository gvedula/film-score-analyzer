# Validation notes: cue.wav (D minor, 90 BPM, 4/4, ~3:02)

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

## Answer key (from session, not memory)
- 33: main section lands
- 94: low strings enter
- 104: beat drop
- 137: tail begins, no pulse
- Memory originally said the main section started at 29; the session
  says 33. Answer keys have to come from the session

## Segmentation (agglomerative, k=5, chroma + MFCC)
- Boundaries: 0.0, 33.6, 98.7, 140.4, 174.7
- Hit: 33 vs 33.6
- Transition 94 (low strings) to 104 (beat drop): one boundary at
  98.7, halfway between. Clustering splits gradual transitions down
  the middle and misses both edges
- Near miss: 137 vs 140.4, just outside the standard 3s window
- Split off the fade at 174.7 as its own section; did not split off
  the silence before the opening hit
- Limitation: had to be told the number of sections

## Novelty detection, 4s window
- Missed all section boundaries (33, 94, 104, 137)
- Found peaks at 55.2, 65.9, 76.5, 87.2, ~10.7s apart
- 4 bars at 89.1 BPM = 10.8s. Confirmed something changes every
  4 bars in the main section. Detected phrase structure, not sections

## Novelty detection, 8s window
- Peaks: 19.6, 30.8, 45.3, 55.9, 66.0, 76.9, 87.7, 139.6
- Hit: 33 vs 30.8 (weak peak)
- Hit: 137 vs 139.6, the strongest peak in the cue
- Missed 94 and 104. Only a weak bump near 97, close to where
  agglomerative put its boundary (98.7). Two methods agree the
  features see one mild change there, not two events
- 4 bar phrase peaks persisted at both window sizes
- 104 to 137 has the lowest novelty in the cue: the climax is the
  most internally consistent section
- First and last 8s are blind spots, the window can't extend past
  the edges of the file
- Likely cause of the 104 miss: the beat drop is a rhythmic change,
  and averaged chroma + MFCC can't see rhythm

## Scorecard (3s tolerance)
- Agglomerative: 1 of 4 (33)
- Novelty 8s: 2 of 4 (33, 137)

## Caveat
- Every parameter so far (2% threshold, 8s window) was tuned on
  this one cue. Needs testing on other cues before trusting it

## Ideas for later
- Add a rhythm feature so the beat drop at 104 is detectable
- Detect which sections are rhythmically driven vs free
- Smaller hop length for finer tempo resolution
- Test on 2 to 3 more cues in different styles