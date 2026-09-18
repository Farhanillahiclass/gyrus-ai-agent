"""
voice.py — microphone input (speech-to-text) and spoken replies (text-to-speech).
Fully offline TTS via pyttsx3. Speech recognition uses Google's free web speech API
under the hood (via SpeechRecognition), which needs internet but no API key.
"""

import speech_recognition as sr
import pyttsx3

_recognizer = sr.Recognizer()
_engine = pyttsx3.init()
_engine.setProperty("rate", 175)


def speak(text: str):
    """Speak text out loud. Also prints it, since not everyone runs with sound on."""
    print(f"Gyrus: {text}")
    try:
        _engine.say(text)
        _engine.runAndWait()
    except Exception as e:
        print(f"[voice] TTS failed silently: {e}")


def listen(timeout=6, phrase_time_limit=12, language="ur-PK") -> str:
    """
    Listen from the default microphone and return recognized text.
    language: 'ur-PK' for Urdu, 'en-US' for English. Falls back to English on failure.
    Returns "" if nothing understood.
    """
    with sr.Microphone() as source:
        print("🎙  Listening...")
        _recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""

    for lang in (language, "en-US"):
        try:
            return _recognizer.recognize_google(audio, language=lang)
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"[voice] Speech service error: {e}")
            return ""
    return ""


if __name__ == "__main__":
    speak("Salaam! Gyrus voice module test chal raha hai.")
    text = listen()
    print("You said:", text or "(nothing recognized)")
