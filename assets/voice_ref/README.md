# StickFacts Brand Voice Reference Assets

Drop your 10-second reference audio samples here to permanently lock in the "StickFacts Brand Voice".

### Default Active Reference:
- `stickfacts_brand_voice.wav`: Reference audio sample (10s studio voice recording).
- `stickfacts_brand_voice.txt`: Transcription matching the audio exactly.

### Custom Voice Cloning Instructions:
1. Record a high-quality 5–12 second `.wav` file of your desired narrator speaking naturally with energy.
2. Place the file here (e.g. `my_voice.wav`).
3. Save a companion text file with the exact spoken words (e.g. `my_voice.txt`).
4. In `voice_tool.py`, pass `ref_audio="pipeline_bridge/assets/voice_ref/my_voice.wav"` or drop it as `stickfacts_brand_voice.wav` to make it the default!
