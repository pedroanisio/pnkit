# Runs only inside one sr-gpu short ticket: sequential native 3.5-second examples, measured total below two minutes.
from pathlib import Path
import subprocess,json,time,hashlib
root=Path(__file__).resolve().parents[1];started=time.monotonic();results=[]
for slug in json.loads((root/'work/gpu-batch-slugs.json').read_text()):
    folder=root/slug;source=hashlib.sha256((folder/'scene.xml').read_bytes()).hexdigest()
    with (folder/'encode.json').open('w') as report,(folder/'encode.log').open('w') as log:
        p=subprocess.run(['/home/pals/.local/share/scene-render/bin/scene-render-premium','encode',str(folder/'scene.xml'),'-o',str(folder/'clip.mp4'),'--hw','nvenc','--parallel','1','--strict','--no-upload','--quality','final','--json'],stdin=subprocess.DEVNULL,stdout=report,stderr=log)
    if p.returncode:raise RuntimeError(slug+': '+(folder/'encode.log').read_text())
    data=json.loads((folder/'encode.json').read_text());assert hashlib.sha256((folder/'scene.xml').read_bytes()).hexdigest()==source
    results.append(dict(slug=slug,scene_sha256=source,render_fps=data['render_fps'],seconds=data['seconds']));print(json.dumps(results[-1]),flush=True)
(root/'work/gpu-batch-results.json').write_text(json.dumps(dict(total_seconds=time.monotonic()-started,results=results),indent=2));(root/'work/gpu-batch.done').write_text('PASS')
