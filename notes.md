# Validation notes: cue.wav (D minor, 90 BPM, ~3:02)

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
- CONFIRM: is the tail free/unmetered? If so, the tracker correctly
  lost the pulse

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

## Ideas for later
- Detect which sections are rhythmically driven vs free
- Smaller hop length for finer tempo resolution
- Test on 2 to 3 more cues in different styles