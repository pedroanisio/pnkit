import build_wave2
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
binary='/home/pals/.local/share/scene-render/bin/scene-render-premium'
items=build_wave2.b.catalog[8:]
with (root/'work/wave2-validation.log').open('w') as log:
    p=subprocess.run([binary,'validate',*[str(root/x['slug']/'scene.xml') for x in items]],stdin=subprocess.DEVNULL,stdout=log,stderr=log)
print('Validate exit:',p.returncode,flush=True)
subprocess.run([sys.executable,str(root/'work/render_stills.py'),*[x['slug'] for x in items]],stdin=subprocess.DEVNULL,check=True)
