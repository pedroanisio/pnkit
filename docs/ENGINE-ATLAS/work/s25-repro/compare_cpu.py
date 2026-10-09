from pathlib import Path
import subprocess,json,time,os
from PIL import Image
import numpy as np
r=Path(__file__).resolve().parent;pin='/home/pals/.local/share/scene-render/bin/scene-render-premium';env=os.environ.copy();env['SR_GPU_BACKEND']='vulkan';results=[]
for name in ['full','pruned']:
 if name=='pruned':
  start=time.monotonic()
  with (r/'pruned-render.log').open('w') as log:p=subprocess.run([pin,'render',str(r/'pruned.scene.xml'),'-t','0.5','-o',str(r/'pruned.png'),'--stats','--strict','--quality','final'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,env=env)
  assert p.returncode==0,(r/'pruned-render.log').read_text();print('PRUNED_STILL_SECONDS',time.monotonic()-start,flush=True)
 start=time.monotonic()
 with (r/(name+'-bench.log')).open('w') as log:p=subprocess.run([pin,'render',str(r/(name+'.scene.xml')),'--frames','15..21','--bench','--stats','--strict','--quality','final'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,env=env)
 assert p.returncode==0,(r/(name+'-bench.log')).read_text();results.append({'name':name,'elapsed':time.monotonic()-start});print(results[-1],flush=True)
a=np.array(Image.open(r/'full.png').convert('RGBA'),dtype=np.int16);b=np.array(Image.open(r/'pruned.png').convert('RGBA'),dtype=np.int16);d=np.abs(a-b);proof={'batches':results,'frame0_5_rgba_max_delta':int(d.max()),'different_components':int((d!=0).sum()),'mean_delta':float(d.mean())};(r/'compare.json').write_text(json.dumps(proof,indent=2));print(proof,flush=True)
