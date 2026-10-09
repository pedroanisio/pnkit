from pathlib import Path
import subprocess,json,time,os,re
from PIL import Image
import numpy as np
r=Path(__file__).resolve().parent;pin='/home/pals/.local/share/scene-render/bin/scene-render-premium';env=os.environ.copy();env['SR_GPU_BACKEND']='vulkan';times=[0,.5,13.19,13.24,14,16.555,21.5,23.826,24,24.326,25.3,33.8,37.9,38.012,39,40.122,44,49,51.9,52];checks=[]
def eval_graph(name,t):
 p=subprocess.run([pin,'eval',str(r/(name+'.scene.xml')),'-t',str(t),'--format','json'],stdin=subprocess.DEVNULL,capture_output=True,text=True,env=env);assert p.returncode==0,p.stderr;return json.loads(p.stdout)
def visible_nodes(g):
 out={}
 for n in g['nodes']:
  if n['kind']=='object3D' and n.get('draw') and n['world_opacity']>0:
   c={k:v for k,v in n.items() if k not in ['parent','transform_parent']};out[n['id']]=c
 return out
for t in times:
 a=eval_graph('full',t);b=eval_graph('condition',t);assert visible_nodes(a)==visible_nodes(b),('visible graph changes',t)
 checks.append({'t':t,'visible_objects':len(visible_nodes(a)),'full_objects':sum(n['kind']=='object3D' for n in a['nodes']),'condition_objects':sum(n['kind']=='object3D' for n in b['nodes'])});print(checks[-1],flush=True)
metrics=[]
for t in [.5,14,39]:
 imgs=[]
 for name in ['full','condition']:
  out=r/f'{name}-{t}.png';start=time.monotonic()
  with (r/f'{name}-{t}-render.log').open('w') as log:p=subprocess.run([pin,'render',str(r/(name+'.scene.xml')),'-t',str(t),'-o',str(out),'--stats','--strict','--quality','final'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,env=env)
  assert p.returncode==0,(r/f'{name}-{t}-render.log').read_text();imgs.append(np.array(Image.open(out).convert('RGBA'),dtype=np.int16));print('STILL',name,t,time.monotonic()-start,flush=True)
 delta=np.abs(imgs[0]-imgs[1]);row={'t':t,'rgba_max_delta':int(delta.max()),'different_components':int((delta!=0).sum())};metrics.append(row);assert row['rgba_max_delta']==0,row;print(row,flush=True)
with (r/'condition-bench.log').open('w') as log:p=subprocess.run([pin,'render',str(r/'condition.scene.xml'),'--frames','15..21','--bench','--stats','--strict','--quality','final'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,env=env)
assert p.returncode==0,(r/'condition-bench.log').read_text();proof={'graph_checks':checks,'pixel_checks':metrics,'scope':'Pinned premium on llvmpipe server2; condition scene is a copy; original film unchanged. GPU throughput for workaround not measured.'};(r/'condition-proof.json').write_text(json.dumps(proof,indent=2));print('PASS',flush=True)
