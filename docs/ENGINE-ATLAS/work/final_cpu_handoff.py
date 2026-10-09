import subprocess,sys
subprocess.run([sys.executable,'work/final_cpu.py'],stdin=subprocess.DEVNULL,check=True)
subprocess.run([sys.executable,'work/review_stills.py'],stdin=subprocess.DEVNULL,check=True)
subprocess.run([sys.executable,'work/review_motion.py'],stdin=subprocess.DEVNULL,check=True)
