import build_showcase
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'work/render_stills.py'),'01-pbr-key-rim','03-dof-focus-pull','06-materials','08-grade-lut-look'],stdin=subprocess.DEVNULL,check=True)
