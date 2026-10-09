import build_wave2
import subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for slug in ['13-soft-physics','25-glsl-volume','26-rich-2d-count']:
    p=subprocess.run(['/home/pals/.local/share/scene-render/bin/scene-render-premium','validate',str(root/slug/'scene.xml')],stdin=subprocess.DEVNULL,capture_output=True,text=True)
    print(slug,'validate',p.returncode,p.stdout,p.stderr,flush=True)
    if p.returncode: raise SystemExit(p.returncode)
subprocess.run([sys.executable,str(root/'work/render_stills.py'),'13-soft-physics','25-glsl-volume','26-rich-2d-count'],stdin=subprocess.DEVNULL,check=True)
