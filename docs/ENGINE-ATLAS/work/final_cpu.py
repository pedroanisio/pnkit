from pathlib import Path
import subprocess,sys,json
root=Path(__file__).resolve().parents[1];binary='/home/pals/.local/share/scene-render/bin/scene-render-premium'
items=json.loads((root/'work/catalog.json').read_text())
for item in items:
    folder=root/item['slug']
    for name in ['scene.xml','still.png']+(['clip.mp4','encode.json'] if item['motion'] else []):
        if not (folder/name).exists(): raise RuntimeError(str(folder/name)+' missing')
validation=[]
for item in items:
    p=subprocess.run([binary,'validate',str(root/item['slug']/'scene.xml')],stdin=subprocess.DEVNULL,capture_output=True,text=True)
    validation.append(dict(slug=item['slug'],exit=p.returncode,output=p.stdout+p.stderr))
(root/'work/final-validation.json').write_text(json.dumps(validation,indent=2))
if any(x['exit'] for x in validation): raise RuntimeError('validation failed')
for name in ['verify_audio_count.py','sample_clips.py','package_atlas.py']:
    subprocess.run([sys.executable,str(root/'work'/name)],stdin=subprocess.DEVNULL,check=True)
qa=json.loads((root/'work/video-checks.json').read_text())
if len(qa)!=25 or not all(x['technical_pass'] and x['strict_clean'] for x in qa): raise RuntimeError('video checks failed')
freeze=root/'work/handoff3';freeze.mkdir(exist_ok=True)
for name in ['SHA256SUMS','CONTACT-SHEET.jpg','README.md','ISSUES.md']:
    (freeze/name).write_bytes((root/name).read_bytes())
for name in ['video-checks.json','sampling.json','catalog.json','audio-count-checks.json','final-validation.json']:
    (freeze/name).write_bytes((root/'work'/name).read_bytes())
print('FINAL: 26 XMLs, 26 stills, 25 clipes, strict e checagens técnicas limpos',flush=True)
