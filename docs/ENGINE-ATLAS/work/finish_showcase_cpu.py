import build_showcase_extra
import subprocess,sys
subprocess.run([sys.executable,'work/render_stills.py','04-25d-parallax','07-particles-path-alpha','08-grade-lut-look'],stdin=subprocess.DEVNULL,check=True)
subprocess.run([sys.executable,'work/comparisons_cpu.py'],stdin=subprocess.DEVNULL,check=True)
