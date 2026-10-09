from pathlib import Path
import subprocess,json
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[1]; checks={}
checks['visible_count']=dict(checks='26-rich-2d-count/count-check.json',pass_check=all(x['pass_check'] for x in json.loads((root/'26-rich-2d-count/count-check.json').read_text())))
folder=root/'22-audio-reactive'; video=folder/'clip.mp4'
if video.exists():
    out=folder/'samples-audio';out.mkdir(exist_ok=True); measures=[]
    for t in [.125,.333333,1.125,1.833333,2.333333,2.583333,3.333333]:
        name=out/(str(t)+'.png')
        subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-ss',str(t),'-i',str(video),'-frames:v','1','-y',str(name)],stdin=subprocess.DEVNULL,check=True)
        a=np.array(Image.open(name).convert('RGB'))[550:1600]
        pixels=int(((a[:,:,1]>100)&(a[:,:,0]<100)&(a[:,:,2]>80)).sum());measures.append(dict(time=t,circle_pixels=pixels))
        if t==1.833333: (folder/'still.png').write_bytes(name.read_bytes())
    p=subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(video),'-vn','-f','f32le','-ac','1','-ar','48000','pipe:1'],stdin=subprocess.DEVNULL,capture_output=True,check=True)
    audio=np.frombuffer(p.stdout,'<f4'); rms=float(np.sqrt(np.mean(audio.astype(float)**2)))
    ratio=max(m['circle_pixels'] for m in measures)/min(m['circle_pixels'] for m in measures)
    checks['audio_reactive']=dict(samples=measures,area_ratio=ratio,decoded_audio_samples=len(audio),rms=rms,pass_check=ratio>1.2 and rms>.001)
(root/'work/audio-count-checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks))
if not all(c['pass_check'] for c in checks.values()): raise SystemExit(1)
