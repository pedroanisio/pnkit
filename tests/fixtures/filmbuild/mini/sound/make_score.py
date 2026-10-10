"""a deterministic stand-in score for the test fixture: 5 s of a quiet 220 Hz sine, 16-bit mono 8 kHz"""
import math, struct, sys, wave
w = wave.open(sys.argv[1], "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
w.writeframes(b"".join(struct.pack("<h", v) for v in (int(3000 * math.sin(2 * math.pi * 220 * i / 8000)) for i in range(8000 * 5))))
w.close()
