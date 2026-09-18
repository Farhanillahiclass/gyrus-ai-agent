"""
mood.py — a *rough* heuristic mood guess from voice recording energy/pitch variance.
This is NOT real emotion AI — no small local model is bundled — it's a simple
signal-processing heuristic (loudness + pitch variability) that gives a decent
"energetic vs flat vs stressed" guess, useful for light personalization only.
Do not use this for anything clinical or high-stakes.
"""

import numpy as np


def guess_mood_from_audio(audio_data: np.ndarray, sample_rate: int = 16000) -> str:
    """audio_data: 1-D numpy array of raw audio samples (e.g. from SpeechRecognition's
    AudioData.get_raw_data() converted to numpy)."""
    if audio_data.size == 0:
        return "neutral"

    energy = np.sqrt(np.mean(audio_data.astype(np.float64) ** 2))
    zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_data)))) / len(audio_data)

    if energy > 3000 and zero_crossings > 0.1:
        return "energetic / excited"
    elif energy < 800:
        return "low / tired"
    elif zero_crossings > 0.15:
        return "stressed / rushed"
    else:
        return "neutral / calm"


if __name__ == "__main__":
    fake_audio = (np.random.randn(16000) * 1000).astype(np.int16)
    print(guess_mood_from_audio(fake_audio))
