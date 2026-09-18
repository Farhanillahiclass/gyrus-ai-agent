"""
main.py — Gyrus's CLI entry point (voice or text). For the 3D dashboard
instead, run server.py and open dashboard/index.html — see README.md.

Usage:
    python main.py            # voice mode
    python main.py --text     # type instead of speaking
"""

import argparse
import voice
import commands
from modules import tasks, notes, user_profile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", action="store_true", help="Type instead of using the microphone")
    args = parser.parse_args()
    text_mode = args.text

    def confirm_fn(prompt):
        voice.speak(prompt)
        answer = input("Confirm (yes/no): ") if text_mode else voice.listen()
        return answer.strip().lower() in commands.CONFIRM_WORDS

    def ask_fn(prompt):
        voice.speak(prompt)
        return input("> ") if text_mode else voice.listen()

    tasks.start_reminder_thread(speak_fn=voice.speak)
    print("=" * 44)
    print("  Gyrus — Powered by MRS Official")
    print("  github.com/Farhanillahiclass")
    print("=" * 44)

    if user_profile.is_known_user():
        name = user_profile.get_fact("name")
        voice.speak(f"Salaam {name}! Main Gyrus hoon. Kya madad kar sakta hoon?")
    else:
        voice.speak("Salaam! Main Gyrus hoon, aap ka assistant. Aap ka naam kya hai?")
        name_input = input("You: ").strip() if text_mode else voice.listen()
        if name_input:
            user_profile.set_fact("name", name_input.title())
            voice.speak(f"Khushi hui {name_input}! Ab hum shuru karte hain.")

    while True:
        try:
            cmd = input("You: ").strip() if text_mode else voice.listen()
            if not cmd:
                continue
            if cmd.lower() in ("exit", "quit", "bye", "band karo"):
                voice.speak("Allah Hafiz!")
                break

            reply = commands.handle(cmd, confirm_fn=confirm_fn, ask_fn=ask_fn)
            if reply == "note-dictation-trigger":
                path = notes.dictate(voice.listen, voice.speak)
                voice.speak(f"Note save ho gaya: {path}")
            else:
                voice.speak(reply)
        except KeyboardInterrupt:
            voice.speak("Allah Hafiz!")
            break


if __name__ == "__main__":
    main()
