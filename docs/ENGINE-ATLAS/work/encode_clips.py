from pathlib import Path
import subprocess, json, os, time, sys
root=Path(__file__).resolve().parents[1]
items=json.loads((root/'work/catalog.json').read_text())
results=[]
for item in items:
    if sys.argv[1:] and item['slug'] not in sys.argv[1:]: continue
    if not item['motion']: continue
    folder=root/item['slug']; started=time.monotonic()
    env=os.environ.copy(); env.update(SR_AGENT='cx-engine',SR_GPU_SHORT='1')
    with (folder/'encode.json').open('w') as report, (folder/'encode.log').open('w') as log:
        p=subprocess.run(['/home/pals/.local/share/scene-render/bin/sr-gpu','/home/pals/.local/share/scene-render/bin/scene-render-premium','encode',str(folder/'scene.xml'),'-o',str(folder/'clip.mp4'),'--hw','nvenc','--parallel','1','--strict','--no-upload','--quality','final','--json'],stdin=subprocess.DEVNULL,stdout=report,stderr=log,env=env)
    entry=dict(slug=item['slug'],exit=p.returncode,queue_and_wall_seconds=round(time.monotonic()-started,3))
    results.append(entry); (root/'work/encode-results.json').write_text(json.dumps(results,indent=2))
    try:
        data=json.loads((folder/'encode.json').read_text()); entry['report']=data
    except Exception: pass
    print(json.dumps(entry),flush=True)
