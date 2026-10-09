from pathlib import Path
import subprocess, json, time, sys
root=Path(__file__).resolve().parents[1]
binary='/home/pals/.local/share/scene-render/bin/scene-render-premium'
results=[]
for item in json.loads((root/'work/catalog.json').read_text()):
    if sys.argv[1:] and item['slug'] not in sys.argv[1:]: continue
    folder=root/item['slug']; t=time.monotonic()
    with (folder/'render.log').open('w') as log:
        p=subprocess.run([binary,'render',str(folder/'scene.xml'),'--time',str(item['still']),'-o',str(folder/'still.png'),'--strict','--quality','final'],stdin=subprocess.DEVNULL,stdout=log,stderr=log)
    results.append(dict(slug=item['slug'],exit=p.returncode,wall_seconds=round(time.monotonic()-t,3)))
    (folder/'still-metrics.json').write_text(json.dumps(results[-1],indent=2))
    (root/'work/still-results.json').write_text(json.dumps(results,indent=2))
    print(results[-1],flush=True)
if any(x['exit'] for x in results): raise SystemExit(1)
