from pathlib import Path
import subprocess,json,time,os
root=Path(__file__).resolve().parent;pin='/home/pals/.local/share/scene-render/bin/scene-render-premium';env=os.environ.copy();env['SR_GPU_BACKEND']='vulkan'
started=time.monotonic();p=subprocess.run([pin,'eval',str(root/'full.scene.xml'),'-t','0.5','--format','json'],stdin=subprocess.DEVNULL,capture_output=True,text=True,env=env);(root/'full-frame.json').write_text(p.stdout);(root/'eval.log').write_text(p.stderr);assert p.returncode==0,p.stderr
g=json.loads(p.stdout);print('EVAL_SECONDS',time.monotonic()-started,'topkeys',list(g),flush=True)
nodes=g['nodes'];objects=[n for n in nodes if n['kind']=='object3D'];print('OBJECTS',len(objects),'zero',sum(n.get('world_opacity',n.get('worldOpacity',1))<=0 for n in objects),flush=True);print('SAMPLE',objects[6:9],flush=True)
started=time.monotonic()
with (root/'full-render.log').open('w') as log:p=subprocess.run([pin,'render',str(root/'full.scene.xml'),'-t','0.5','-o',str(root/'full.png'),'--stats','--strict','--quality','final'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,env=env)
print('FULL_RENDER_SECONDS',time.monotonic()-started,'EXIT',p.returncode,flush=True);assert p.returncode==0,(root/'full-render.log').read_text()[-5000:]
