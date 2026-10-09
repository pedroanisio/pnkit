import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'work/package_atlas.py'),'--wave1'],stdin=subprocess.DEVNULL,check=True)
subprocess.run([sys.executable,str(root/'work/sample_clips.py')],stdin=subprocess.DEVNULL,check=True)
freeze=root/'work/handoff1';freeze.mkdir(exist_ok=True)
for name in ['SHA256SUMS','CONTACT-SHEET.jpg','README.md']:
    (freeze/name).write_bytes((root/name).read_bytes())
for name in ['video-checks.json','sampling.json','catalog.json']:
    (freeze/name).write_bytes((root/'work'/name).read_bytes())
