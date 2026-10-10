#!/usr/bin/env python3
"""A recorded-take stand-in for the voice stage's TTS command (no ElevenLabs call): writes a silent WAV of 0.4 s per
spoken word and the words file {"duration", "words": [[word, start, end]]} for the spoken text it is given.
    fixture_tts.py SCENE TEXT_FILE OUT_WAV OUT_WORDS"""
import json, sys, wave
scene, text, wav, words = sys.argv[1:5]
ws = open(text, encoding="utf-8").read().split()
with wave.open(wav, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000); w.writeframes(b"\0\0" * int(8000 * 0.4 * len(ws)))
json.dump({"duration": round(0.4 * len(ws), 3), "words": [[x, round(0.4 * i, 3), round(0.4 * i + 0.35, 3)] for i, x in enumerate(ws)]},
          open(words, "w", encoding="utf-8"), ensure_ascii=False)
